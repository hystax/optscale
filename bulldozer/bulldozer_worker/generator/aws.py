import os
import logging
import pymustache

from bulldozer.bulldozer_worker.exceptions import NotSupportedException

LOG = logging.getLogger(__name__)


class DefaultImageNotSupported(Exception):
    pass


class TFGenerator:

    reserved_tags = ["Name", "Seed"]

    # default images by region id
    aws_image_region_map = {
        "us-east-1": "ami-0261755bbcb8c4a84",
        "us-east-2": "ami-0430580de6244e02e",
        "us-west-1": "ami-04d1dcfb793f6fa37",
        "us-west-2": "ami-0c65adc9a5c1b5d7c",
        "ca-central-1": "ami-0940df33750ae6e7f",
        "eu-central-1": "ami-0ab1a82de7ca5889c",
        "eu-west-1": "ami-0136ddddd07f0584f",
        "eu-west-2": "ami-007ec828a062d87a5",
        "eu-south-1": "ami-0db8d6245dc15335a",
        "eu-west-3": "ami-008bcc0a51a849165",
        "eu-north-1": "ami-08766f81ab52792ce",
        "sa-east-1": "ami-0f47fe3e9defb4cbf",
        "ap-southeast-3": "ami-0dea4c77aa6baff5a",
        "ap-south-1": "ami-08e5424edfe926b43",
        "ap-northeast-3": "ami-0c5a66cf375fc12d8",
        "ap-northeast-2": "ami-04341a215040f91bb",
        "ap-southeast-1": "ami-002843b0a9e09324a",
        "ap-southeast-2": "ami-0d02292614a3b0df1",
        "ap-northeast-1": "ami-0ed99df77a82560e6",
    }

    def __init__(self, seed,
                 name,
                 image,
                 region,
                 instance_type,
                 volume_size_gb,
                 user_data=None,
                 key=None,
                 tags=None,
                 open_ingress=False,
                 ):
        if tags is None:
            tags = dict()

        self.seed = seed
        self.name = name
        self._image = image
        self.region = region
        self.key = bool(key)
        self.key_name = key
        self.instance_type = instance_type
        self.volume_size_gb = volume_size_gb
        self.user_data = user_data
        self.tags = tags
        self.open_ingress = open_ingress

    @property
    def image(self):
        if self._image is None:
            image = self.aws_image_region_map.get(self.region)
            if not image:
                raise DefaultImageNotSupported(
                    "default image for region %s not supported" % self.region)
            self._image = image
        return self._image

    def generate_payload(self, spot=False):

        tags = [
            {"name": "Name", "val": self.name},
            {"name": "Seed", "val": self.seed}
        ]
        for k, v in self.tags.items():
            if k not in self.reserved_tags:
                tags.append({"name": k, "val": v})
            else:
                LOG.warning(
                    "skipping setting tag: %s because it's reserved", k
                )
        d = {
            "use_spot": spot,
            "name": self.name,
            "seed": self.seed,
            "image": self.image,
            "region": self.region,
            "key": self.key,
            "key_name": self.key_name,
            "instance_type": self.instance_type,
            "volume_size_gb": self.volume_size_gb,
            "tags": tags,
            "open_ingress": self.open_ingress,
        }
        if self.user_data:
            d.update({"user_data": self.user_data})
        return d


class TFGeneratorAWS(TFGenerator):
    template_file = os.path.join(os.path.dirname(__file__), "templates", "aws.tft")

    def get_generate_func(self):
        return self.generate_payload()

    def render(self):
        with open(self.template_file, 'r') as fh:
            template = fh.read()
        return pymustache.render(template, self.get_generate_func())


class TFGeneratorAWSSpot(TFGeneratorAWS):
    def get_generate_func(self):
        return self.generate_payload(spot=True)


class TFGeneratorFactory:

    TFGEN_MAP = {
        "AWS": TFGeneratorAWS,
        "AWS_SPOT": TFGeneratorAWSSpot,
    }

    @classmethod
    def get_generator(cls, platform):
        tfg = cls.TFGEN_MAP.get(platform)
        if not tfg:
            raise NotSupportedException("%s not supported", platform)
        return tfg
