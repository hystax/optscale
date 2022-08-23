import React from "react";
import PropTypes from "prop-types";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const Markdown = ({ children }) => (
  <ReactMarkdown
    components={{
      a: ({ children: markdownChildren, href }) => (
        <a href={href} target="_blank" rel="noopener noreferrer">
          {markdownChildren}
        </a>
      )
    }}
    remarkPlugins={[remarkGfm]}
  >
    {children}
  </ReactMarkdown>
);

Markdown.propTypes = {
  children: PropTypes.node.isRequired
};

export default Markdown;
