# BEM stylesheet structure

`main.css` is the single delivery bundle for this small server-rendered application. Its selectors follow BEM roles: standalone blocks (`site-header`, `hero`, `button`, `ticket-table`, `comment`), elements (`site-header__nav`, `hero__lead`, `field__error`), and modifiers (`button--secondary`, `badge--critical`, `comment--internal`). Utility-like layout blocks (`container`, `page`, `muted`) are intentionally limited and documented here rather than mixed into component names.

If the UI grows, split the bundle without changing class names:

```text
css/
  base/       reset.css, tokens.css, typography.css
  layout/     container.css, page.css
  blocks/     button.css, ticket-table.css, comment.css, ...
  main.css    ordered imports only
```
