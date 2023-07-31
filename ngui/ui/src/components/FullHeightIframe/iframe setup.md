# Custom iframe component usage
## Iframe (remote) setup
Please, add HTML code below to remote page
```HTML
<script>
    (function () {
        const htmlTag = document.getElementsByTagName("html")[0]; 
        const editor = document.getElementsByTagName("BODY")[0].className.lastIndexOf("elementor-editor") != -1;

        const isIframed = () => {
            try {
                return window.self !== window.top;
            } catch (e) {
                return true;
            }
        }

        if (!isIframed() && !editor) {
            window.location.href = "/"
        }

        const postHeightMessage = () => {
            const height = htmlTag.getBoundingClientRect().height;
            window.parent.postMessage({ iframeHeight: height }, "*");
        }

        window.addEventListener('load', (event) => {
            // adding "iframed" class to fix strange +1px scroll
            if (isIframed) {
                htmlTag.className += " iframed";
            }

            postHeightMessage();

            window.addEventListener('resize', postHeightMessage);
        });

    }());
</script>

<style>
    #cookie-notice {
        display: none !important;
    }

    html.iframed {
        overflow: hidden;
    }
</style>
```
It will
- Redirect to / page if page loaded not inside an iframe or elementor editor
- Post message with { iframeHeight }, where iframeHeight is bounding client rect height of html tag
- Hide cookie-notice plugin

## Iframe (component) setup
Just set source property, after the first recieved message with iframeHeight, loader will be replaced with iframe content.