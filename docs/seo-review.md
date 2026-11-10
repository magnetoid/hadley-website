# Hadley technical SEO review

Scope: preserve every existing section's visible text, photographs and biographies; replace JS-only pseudo-pages with crawlable static documents.

## Implemented
Seven server-rendered HTML documents: /, /about/, /services/, /experience/, /insights/, /team/, /contact/. Navigation/footer/CTA links use real hrefs. Each document includes only its own section, a main landmark, a primary heading, unique title and description, self-canonical, matching social URL and WebPage/AboutPage/ContactPage schema. Sitemap lists all seven canonical URLs. Existing robots and genuine 404 routing retained. Mobile keyboard navigation improved. Docker explicitly copies all documents.

## Evidence
Builder compares each page's text with the original section and aborts if changed. Local checks cover links, image paths (including query strings), main/h1 presence and JavaScript syntax. Team page opened in browser successfully.

## Findings outside this change
Contact form currently only displays a confirmation through client-side JavaScript; no backend delivery was found. Do not treat this as a functioning enquiry-delivery system. Needs a separately tested delivery implementation.
Insights has existing teaser content rather than full articles; no fabricated article pages were generated. Further content expansion requires editorial approval.
Search Console ownership, sitemap submission, indexing and real-user Core Web Vitals require separate account access/measurement. No ranking or indexing guarantee. No invented reviews, local addresses or Person credentials added.

## Google documentation directly reviewed
- https://developers.google.com/search/docs/crawling-indexing/links-crawlable — real anchor href URLs and internal discoverability.
- https://developers.google.com/search/docs/appearance/title-link — distinctive descriptive document titles.
- https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls — consistent internal URLs, canonical and sitemap signals.
- https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap — absolute canonical URLs in root XML sitemap.
- https://developers.google.com/search/docs/crawling-indexing/javascript/javascript-seo-basics — initial HTML content and unique document metadata avoid JS-only discovery dependence.

## Next priorities
1. Wire and test real enquiry delivery without false success messages.
2. Verify Search Console; submit sitemap and inspect representative URLs.
3. Measure mobile field performance and run Lighthouse before making quantified speed claims.
4. Publish genuine approved research articles and link them contextually.
