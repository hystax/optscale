import { Box } from "@mui/material";
import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import ReactMarkdown from "react-markdown";
import remarkDirective from "remark-directive";
import remarkGfm from "remark-gfm";
import { visit } from "unist-util-visit";
import { SPACING_1, SPACING_2 } from "utils/layouts";

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

// TODO: Maybe need to create a component with a length limit
const MarkdownTypography = ({ children, variant, component }) => (
  <Typography variant={variant} component={component}>
    {children}
  </Typography>
);

const DividingHeader = ({ children }) => (
  <Box
    component="span"
    sx={{
      padding: SPACING_1,
      mt: SPACING_2,
      mb: SPACING_2,
      display: "block",
      textAlign: "center",
      backgroundColor: (theme) => theme.palette.info.main,
      color: (theme) => theme.palette.common.white
    }}
  >
    <MarkdownTypography variant="h6" component="span">
      {children}
    </MarkdownTypography>
  </Box>
);

const Markdown = ({ children }) => (
  <ReactMarkdown
    transformImageUri={(uri) => `/docs/${uri}`}
    linkTarget="_blank"
    components={{
      a: ({ children: markdownChildren, href }) => (
        <Link href={href} target="_blank" rel="noopener noreferrer">
          {markdownChildren}
        </Link>
      ),
      h1: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="h5" component="h1">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h2: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="h6" component="h2">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h3: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="subtitle1" component="h3">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h4: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="subtitle1" component="h4">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h5: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="body1" component="h5">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h6: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="body1" component="h6">
          {markdownChildren}
        </MarkdownTypography>
      ),
      p: ({ children: markdownChildren }) => <MarkdownTypography>{markdownChildren}</MarkdownTypography>,
      img: ({ src, alt }) => (
        <Box display="block" component="span" my={SPACING_2}>
          <img style={{ maxWidth: "100%" }} src={src} alt={alt} />
        </Box>
      ),
      DividingHeader
    }}
    remarkPlugins={[remarkGfm, remarkDirective, reactMarkdownRemarkDirective]}
  >
    {children}
  </ReactMarkdown>
);

export default Markdown;
