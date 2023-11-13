import Link from "@mui/material/Link";
import Typography from "@mui/material/Typography";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

// TODO: Maybe need to create a component with a length limit
const MarkdownTypography = ({ children, variant, component }) => (
  <Typography variant={variant} component={component}>
    {children}
  </Typography>
);

const Markdown = ({ children }) => (
  <ReactMarkdown
    linkTarget="_blank"
    components={{
      a: ({ children: markdownChildren, href }) => (
        <Link href={href} target="_blank" rel="noopener noreferrer">
          {markdownChildren}
        </Link>
      ),
      h1: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="h3" component="h1">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h2: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="h4" component="h2">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h3: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="h5" component="h3">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h4: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="h6" component="h4">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h5: ({ children: markdownChildren }) => (
        <MarkdownTypography variant="body1" component="h5">
          {markdownChildren}
        </MarkdownTypography>
      ),
      h6: ({ children: markdownChildren }) => <MarkdownTypography component="h6">{markdownChildren}</MarkdownTypography>,
      p: ({ children: markdownChildren }) => <MarkdownTypography component="p">{markdownChildren}</MarkdownTypography>
    }}
    remarkPlugins={[remarkGfm]}
  >
    {children}
  </ReactMarkdown>
);

export default Markdown;
