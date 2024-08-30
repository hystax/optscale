import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import ReactMarkdown from "react-markdown";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import { visit } from "unist-util-visit";
import { SPACING_2 } from "utils/layouts";

function reactMarkdownRemarkDirective() {
  return (tree) => {
    visit(tree, ["textDirective", "leafDirective", "containerDirective"], (node) => {
      // won't work without reassign.
      // eslint-disable-next-line no-param-reassign
      node.data = {
        hName: node.name,
        hProperties: node.attributes,
        ...node.data
      };
      return node;
    });
  };
}

const Markdown = ({ children, transformImageUri }) => (
  <ReactMarkdown
    transformImageUri={(uri) => (typeof transformImageUri === "function" ? transformImageUri(uri) : uri)}
    linkTarget="_blank"
    components={{
      a: ({ children: markdownChildren, href }) => (
        <Link href={href} target="_blank" rel="noopener noreferrer">
          {markdownChildren}
        </Link>
      ),
      h1: ({ children: markdownChildren }) => (
        <Typography variant="h6" component="h1" gutterBottom>
          {markdownChildren}
        </Typography>
      ),
      h2: ({ children: markdownChildren }) => (
        <Typography variant="h6" component="h2" gutterBottom>
          {markdownChildren}
        </Typography>
      ),
      h3: ({ children: markdownChildren }) => (
        <Typography variant="subtitle1" component="h3" gutterBottom>
          {markdownChildren}
        </Typography>
      ),
      h4: ({ children: markdownChildren }) => (
        <Typography variant="subtitle1" component="h4" gutterBottom>
          {markdownChildren}
        </Typography>
      ),
      h5: ({ children: markdownChildren }) => (
        <Typography variant="body1" component="h5" gutterBottom>
          {markdownChildren}
        </Typography>
      ),
      h6: ({ children: markdownChildren }) => (
        <Typography variant="body1" component="h6" gutterBottom>
          {markdownChildren}
        </Typography>
      ),
      p: ({ children: markdownChildren }) => <Typography gutterBottom>{markdownChildren}</Typography>,
      img: ({ src, alt }) => (
        <Box display="block" component="span" my={SPACING_2}>
          <img style={{ maxWidth: "100%" }} src={src} alt={alt} />
        </Box>
      ),
      li: ({ children: liChildren }) => <Typography component="li">{liChildren}</Typography>,
      ul: ({ children: ulChildren }) => (
        <Typography component="ul" gutterBottom>
          {ulChildren}
        </Typography>
      )
    }}
    remarkPlugins={[remarkGfm, remarkDirective, reactMarkdownRemarkDirective]}
  >
    {children}
  </ReactMarkdown>
);

export default Markdown;
