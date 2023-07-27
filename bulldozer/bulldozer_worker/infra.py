import boto3
import os
import shutil
from typing import Union
import subprocess
import re
import tarfile
import logging

from exceptions import NotSupportedException
from generator.aws import TFGeneratorFactory

LOG = logging.getLogger(__name__)


class InfraException(Exception):
    pass


class Infra:

    template_file = "main.tf"
    platform_dir = ".terraform"
    lock_file = ".terraform.lock.hcl"
    var_file = "variables.tf"
    var_values = "terraform.tfvars"
    tar = "%s.tar.gz"

    LOCK_PATH_MAP = {
        "AWS": os.path.join("locks", "aws", lock_file),
        "AWS_SPOT": os.path.join("locks", "aws", lock_file),
    }

    VAR_PATH_MAP = {
        "AWS": os.path.join("variables", "aws", var_file),
        "AWS_SPOT": os.path.join("variables", "aws", var_file),
    }

    state_files = [template_file, 'terraform.tfstate', 'terraform.tfstate.backup']

    # default workspace
    workspace = "/var/lib/bulldozer/"

    def get_lock_file_path(self):
        return self.LOCK_PATH_MAP.get(self.platform_type)

    def get_var_file_path(self):
        return self.VAR_PATH_MAP.get(self.platform_type)

    @staticmethod
    def extract_outputs(out: str) -> (str, str):
        """
        Extracts vars from terraform outputs
        :param out:
        :return: (instance_id, ip)
        """
        instance_id = ""
        ip = ""
        instance_id_pattern = "instance_id = \"(.+)\""
        ip_pattern = "instance_ip = \"(.+)\""
        outputs = out.strip().split("\n")[-2:]
        for i in outputs:
            id_ = re.findall(instance_id_pattern, i)
            if id_:
                instance_id = id_[0]
            ip_ = re.findall(ip_pattern, i)
            if ip_:
                ip = ip_[0]
        return instance_id, ip

    def save_infra(self, filename: str, path: str):
        """
        Saves infrastructure state to S3-like storage
        :param filename:
        :param path
        :return:
        """
        self.minio_cl.upload_file(
            os.path.join(path, filename),
            self.bucket_name, filename
        )

    def load_infra(self, path: str):
        self.minio_cl.download_file(
            self.bucket_name,
            self.tar % self.seed,
            os.path.join(path, self.tar % self.seed)
        )

    @property
    def generator(self):
        if self._generator is None:
            gen = TFGeneratorFactory.get_generator(self.platform_type)
            if not gen:
                raise NotSupportedException("%s is not supported" % self.platform_type)
            self._generator = gen
        return self._generator

    @property
    def seed(self):
        return self._seed

    @property
    def bucket_name(self) -> str:
        """
        Encapsulates bucket name
        :return:
        """
        return self._bucket_name

    def archive(self, path: str) -> str:
        """
        Creates archive
        :return:
        """
        name = self.seed
        filename = "%s.tar.gz" % name
        os.chdir(path)
        with tarfile.open(filename, "w:gz") as tfh:
            for item in self.state_files:
                try:
                    tfh.add(item, arcname=item)
                except FileNotFoundError:
                    # possible skip state backup
                    LOG.warning("Skipping file %s: not found", item)
                    continue
        os.chdir(os.path.dirname(__file__))
        return filename

    def extract(self, path: str) -> None:
        name = self.seed
        filename = "%s.tar.gz" % name
        os.chdir(path)
        with tarfile.open(filename) as fh:
            fh.extractall()

    def __init__(
            self,
            runner_id: str,
            platform_type: str,
            minio_cl,
            bucket_name: str,
            path: Union[str, None],
            creds=None):
        if creds is None:
            creds = dict()
        self.platform_type = platform_type
        self._generator = None
        self._seed = runner_id
        self._creds = creds
        self._bucket_name = bucket_name
        self._s3cl = None
        if path is None:
            path = self.workspace
        self.path = path
        self.minio_cl = minio_cl

    @property
    def s3cl(self):
        if self._s3cl is None:
            aws_access_key_id = self._creds.get("aws_access_key_id")
            aws_secret_access_key = self._creds.get("aws_secret_access_key")
            self._s3cl = boto3.client(
                's3',
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
            )
        return self._s3cl

    def make_vars(self, path: str):
        file_path = os.path.join(path, self.var_values)
        acc_key = self._creds.get("aws_access_key_id")
        sec_key = self._creds.get("aws_secret_access_key")
        with open(file_path, "w") as fh:
            fh.write('access_key = "%s"\n' % acc_key)
            fh.write('secret_key = "%s"\n' % sec_key)

    @property
    def exe_path(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), 'terraform'))

    def copy_artifacts(self, path: str):
        """
        Copies artifacts (such as provider, lock)
        :return:
        """
        provider_path = os.path.join(os.path.dirname(__file__), self.platform_dir)
        # copy provider
        shutil.copytree(provider_path, os.path.join(path, self.platform_dir))
        # copy lock
        shutil.copyfile(os.path.join(os.path.dirname(__file__), self.get_lock_file_path()),
                        os.path.join(path, self.lock_file))
        # copy var
        shutil.copyfile(os.path.join(os.path.dirname(__file__), self.get_var_file_path()),
                        os.path.join(path, self.var_file))

    def start(
            self,
            name,
            region,
            flavor,
            size_gb,
            user_data,
            image=None,
            key=None,
            tags=None,
            open_ingress=False,
    ):
        gen = self.generator(
            self.seed,
            name,
            image,
            region,
            flavor,
            size_gb,
            user_data,
            key,
            tags,
            open_ingress
        )
        template = gen.render()
        path = os.path.join(os.path.dirname(self.path), self.seed)
        os.makedirs(path, exist_ok=True)
        template_file = os.path.join(path, self.template_file)
        try:
            with open(template_file, "w") as fh:
                fh.write(template)
            self.copy_artifacts(path)
            self.make_vars(path)
            # save plan to the logs
            out = subprocess.check_output([self.exe_path, "apply", "--auto-approve"], cwd=path).decode('UTF-8')
            LOG.info(out)
            LOG.debug("extracting instance id and ip address")
            instance_id, ip_addr = self.extract_outputs(out)
            LOG.info("started instance runner_id: %s -> instance id: %s, ip: %s",
                     self.seed, instance_id, ip_addr)
            # create archive with states
            filename = self.archive(path)
            # upload states
            self.save_infra(filename, path)
            shutil.rmtree(path)
            return instance_id, ip_addr

        except Exception as exc:
            # cleanup
            LOG.error("Infra failed because of %s", str(exc))
            try:
                LOG.info("Cleaning up runner %s", str(self.seed))
                subprocess.check_output([self.exe_path, "destroy", "--auto-approve"], cwd=path).decode('UTF-8')
            except:
                pass
            raise InfraException("Infra exception: %s" % str(exc))
        finally:
            # ensure we cleaned workdir in case of infra failure
            shutil.rmtree(path, ignore_errors=True)

    def load(self) -> str:
        path = os.path.join(self.path, self.seed)
        os.makedirs(path)
        # load infra from s3-like
        self.load_infra(path)
        self.extract(path)
        return path

    def destroy(self):
        path = self.load()
        try:
            self.copy_artifacts(path)
            self.make_vars(path)
            plan = subprocess.check_output(
                [self.exe_path, "destroy", "--auto-approve"], cwd=path).decode('UTF-8')
            LOG.info(plan)
            # by design do not remove states for s3
        finally:
            # cleanup workdir
            shutil.rmtree(path)
