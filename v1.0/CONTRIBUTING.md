# Contributing to CockroachDB Docs

The CockroachDB docs are open source just like the database itself. We welcome your contributions!

## Setup

1. Fork the [CockroachDB docs repository](https://github.com/cockroachdb/docs).

2. [Create a local clone](https://help.github.com/articles/cloning-a-repository/) of your fork.

3. CockroachDB uses [Jekyll](https://jekyllrb.com/docs/installation/) to transform Markdown and layout files into a complete, static HTML site. We also use [HTMLProofer](https://github.com/gjtorikian/html-proofer) to check the generated HTML for errors (broken internal and external links, missing images, etc.).

    Install Jekyll, HTMLProofer, and some other dependencies so you can view doc changes locally:

    ``` shell
    $ cd path/to/docs
    $ make bootstrap
    ```

3. Learn the essentials of our [Docs Structure](#docs-structure).

4. Review our simple [Style Guide](#style-guide).

## Get Started

Once you're ready to contribute:

1. Create a new local branch for your work:

   ``` shell
   $ cd path/to/docs
   $ git checkout -b "<your branch name>"

3. Make your changes.

4. [Build and test the docs locally](#build-and-test-the-docs-locally).

5. Commit your changes.

5. [Push to your local branch to your remote fork](https://help.github.com/articles/pushing-to-a-remote/).

6. Back in the CockroachDB docs repo, [open a pull request](https://github.com/cockroachdb/docs/pulls) and assign it to `jseldess`.

We'll review your changes, providing feedback and guidance as necessary. Also, Teamcity, the system we use to automate tests, will run the markdown files through Jekyll and then run [HTMLProofer](https://github.com/gjtorikian/html-proofer) against the resulting HTML output to check for errors. Teamcity will also attempt to sync the HTML to an AWS server, but since you'll be working on your own fork, this part of the process will fail; don't worry about the Teamcity fail status.

## Keep Contributing

If you want to regularly contribute to the CockroachDB docs, there are a few things we recommend:

1. Make it easy to bring updated docs into your fork by tracking us upstream:

    ``` shell
    $ git remote add --track master upstream https://github.com/cockroachdb/docs.git
    ```

2. When you're ready to make your next round of changes, get our latest docs:

    ``` shell
    $ git fetch upstream
    $ git merge upstream/master
    ```

3. Repeat the write, build, push, pull flow from the [Get Started](#get-started) section above.

## Docs Structure

### Pages

Each docs page must be an `.md` file in the root directory of the repository, must be written in the [kramdown](http://kramdown.gettalong.org/quickref.html) dialect of Markdown, and must start with the following front-matter:

```
---
title: Title of Page
summary: Short description of page for SEO
toc: false
---
```

- `title`: Used as the h1 header.
- `summary`: Used as the page's `meta description` for SEO. Keep this under 155 characters. Consider using the first sentence of the page, or something similar.
- `toc`: Adds an auto-generated table of contents to the page. See [Page TOC](#page-toc) for full details.

Optionally, you can specify in the front-matter a list of allowed hashes
that don't correspond to a section heading on the page. This is
currently used for pages with JavaScript toggle buttons, where the
toggle to activate by default can be specified in the URL hash. If you
attempt to link to, for example, `page-with-toggles.html#toggle-id` without
listing `toggle-id` in `allowed_hashes`, our HTML proofer will complain
that `toggle-id` does not exist on the page. Listing a hash in
`allowed_hashes` will generate a dummy element with that ID at the top
of the page, which keeps our HTML proofer happy.

Here's an example from a page with OS toggles:

```
allowed_hashes: [os-mac, os-linux, os-windows]
```

### Page TOC

The CockroachDB Jekyll theme can auto-generate a page-level table of contents listing all h2 headers or all h2 and h3 headers on the page. Related files: `js/toc.js` and `_includes/toc.html`.

#### TOC Placement

-   To add a page TOC to the very top of the page, set `toc: true` in the page's front-matter.

-   To add a page TOC anywhere else on the page (for example, after an intro paragraph), set `toc: false` in the page's front-matter and add the following HTML where you want the toc to appear on the page:

    ``` html
    <div id="toc"></div>
    ```

-   To omit a page TOC from the page, set `toc: false` in the page's front-matter.

#### TOC Levels

By default, a page TOC includes h2 and h3 headers. To limit a page TOC to h2 headers only, set `toc_not_nested: true` in the page's front-matter.

### Sidebar

The [`_data/sidebar_doc.yml`](_data/sidebar_doc.yml) YAML file controls which pages appear in the docs sidebar. If you're adding a page that you think should appear in the sidebar, please mention this in your pull request.

For each item in the sidebar, there are three possible YAML fields:

Field | Description
------|------------
`title` | The page title, as displayed in the sidebar. This can be different from the actual page title.
`url` | The URL of the page to link to, formatted as `/<page-name>.html`, e.g., `/learn-cockroachdb-sql.html`.
`alternate_urls` | The URLs of other pages that should highlight this title in the sidebar, as a comma-separated list within square brackets, e.g., `[/build-a-go-app-with-cockroachdb-gorm.html]`. It's possible to list alternate URLs one-per-line, [indented appropriately](http://yaml.org/spec/1.2/spec.html#id2759963), but for now, it's recommended to use the bracketed list format instead.

### Auto-Included Content

Some pages auto-include content from the [`_includes`](_includes) directory. For example, each SQL statement page inludes a syntax diagram from `_includes/sql/diagrams`, and the [build-an-app-with-cockroachdb.md](build-an-app-with-cockroachdb.md) tutorials include code samples from `_includes/app`.

The syntax for including content is `{% include <filepath> %}`, for example, `{% include app/basic-sample.rb %}`.

### Asciicasts

1. [Install asciinema](https://asciinema.org/docs/installation).
2. Size your shell window to be a bit narrowing than our code blocks.
3. Initiate an asciicast with `asciinema rec -c "/bin/bash -l"`. This makes the asciicast use your shell's appearance.
4. Press **CTRL + D** to stop recording.
5. Press **Enter** to upload the recording to asciinema.
6. Click **Download**.
7. Rename the `.json` asciicast file and place it in the `/asciicasts` directory.
8. On the page, set `asciicast: true` in the front-matter.
9. On the page, include the following html where you want the asciicast to appear. Change the `src` filepath as relevant, and change `poster` to the time in the asciicast that you want to use as the static image. For other details about customizing the asciicast appearance, see the asciinema [README](https://github.com/asciinema/asciinema-player#asciinema-player-element-attributes).

  ```
  <asciinema-player class="asciinema-demo" src="asciicasts/start-a-local-cluster.json" cols="107" speed="2" theme="solarized-dark" poster="npt:0:30" title="Start a Local Cluster"></asciinema-player>
  ```

### Feedback Widget

We show "Yes/No" feedback buttons at the bottom of every page by default. To remove these buttons from a page, set `feedback: false` in the page's front-matter.

### Contributing Options

We show "Contribute" options in the top-right of every page by default. To remove these options from a page, set `contribute: false` in the page's front-matter.

### A/B Testing

We use [Optimizely](https://www.optimizely.com/) to A/B test changes across our website. To include a page in A/B testing, you must add the necessary JavaScript by setting `optimizely: true` in the page's front-matter.

## Style Guide

CockroachDB docs should be:

- Clear
- Correct
- Concise

To enable this, we have the following specific guidance:

- Use the imperative present tense, also known as "[imperative mood](https://en.wikipedia.org/wiki/Imperative_mood)."
- Use active voice instead of passive. [*Purdue Online Writing Lab resource*](https://owl.english.purdue.edu/owl/resource/539/02/)
- Prefer periods over semicolons.

We also have additional guidance to ensure consistency with our existing documents.

### Code Samples

Code samples are marked with an opening and closing set of 3 tildes (`~~~`). Shell and SQL commands should be syntax highlighted where appropriate using the following info.

#### Shell Code Samples
Start shell code samples with `~~~ shell` followed by a line break. The first character of the next line must be the terminal marker `$`.

#### SQL Code Samples
SQL code samples are broken into two sections: commands and responses.

- **Commands** (e.g., `SELECT`, `CREATE TABLE`) should begin with `~~~ sql` followed by a line break. The first character of the next line must be the terminal marker `>`.
- **Responses** (e.g., retrieved tables) should begin with `~~~` but should *not* be syntax highlighted.

  Note that not all responses warrant inclusion. For example, if a SQL code sample shows `CREATE TABLE`, `INSERT`, and then `SELECT`, it's unnecessary to show the responses for `CREATE TABLE` (which is just `CREATE TABLE`) and `INSERT` (which is just `INSERT <number of rows>`).

### Lists

For each item of a numbered list, use the step number followed by a period, e.g., `1.`.

For each item of a bulleted list, use the `-` character.

#### Nesting Lists

To nest a list under a list item, start the list on the next line (no empty line), and indent the new list four spaces, for example:

```
1. This is a step.
    - This is a bullet.
    - This is a bullet.
    - This is a bullet.

2. This is a step.
```

#### Nesting Paragraphs or Code Blocks

To nest a paragraph or code block under a list item, insert an empty line and then indent the paragraph or code block 4 spaces, for example:

```
1. This is a step.

    This is a nested paragraph.

    ~~~ shell
    $ command
    ~~~
```

Similarly, to nest a paragraph or code block under a *nested* list item, insert an empty line and then indent the paragraph or code block 8 spaces, for example:

```
1. This is a step.
    - This is a bullet.

        ~~~ shell
        $ command
        ~~~
    - This is a bullet.

        ~~~ shell
        $ command
        ~~~
    - This is a bullet.

        ~~~ shell
        $ command
        ~~~

2. This is a step.
```

### Notes, Warnings, & Tips

Our docs use three classes of highlighted text.

**NOTE**: The text of notes, warnings, and tips must be formatted in HTML instead of Markdown/Kramdown.

#### Notes

Use notes to call attention to a piece of clarifying information; this information should not be crucial to accomplishing the task in the document.

For example, you might use a note to let users know that the `DELETE` statement only deletes rows and that to delete columns you must use `ALTER TABLE`. This helps clarify `DELETE`'s purpose and point misguided users to the right place.

To insert a note, use the following code:

```
{{site.data.alerts.callout_info}} <tip text goes here> {{site.data.alerts.end}}
```

#### Warnings

Use warning to express that a piece of information is critical to understand to prevent unexpected things from happening.

For example, you might include a warning that using `CASCADE` in `DROP INDEX` drops dependent objects without warning. This is critical to prevent users from unexpectedly losing constraints or additional indexes.

To insert a warning, use the following code:

```
{{site.data.alerts.callout_danger}} <warning text goes here> {{site.data.alerts.end}}
```

#### Tips

Use tips to highlight nice-to-know pieces of information.

For example, you might include a tip to our Github repo's Terraform scripts on the Google Cloud Engine deployment page. It's nice to know it's there, but doesn't clarify anything nor is it critical.

To insert a tip, use the following code:

```
{{site.data.alerts.callout_success}}{{site.data.alerts.end}}
```

## Build and Test the Docs Locally

Once you've installed Jekyll and have a local clone of the docs repository, you can build and test the docs as follows:

1.  From the root directory of your clone, run:

    ``` shell
    $ make serve
    ```

2.  Point your browser to `http://127.0.0.1:4000/docs/` and manually check your changes.

    - If the page you want to test isn't listed in the sidebar, just point to it directly, for example, `http://127.0.0.1:4000/docs/new-page.html`.

    - When you make additional changes, Jekyll automatically regenerates the HTML content. No need to stop and re-start Jekyll; just refresh your browser.

    Once you're done viewing your changes, use **CTRL + C** to stop the Jekyll server.

3.  Run automated tests against the Jekyll-generate HTML files to check for problems (broken links, missing alt texts for images, etc.):

    ``` shell
    $ make test
    ```