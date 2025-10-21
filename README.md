# RSES / Physics of the Earth PHYS-3070

![Health check](https://github.com/ANU-RSES-Education/PHYS-3070/workflows/Health%20check/badge.svg)

## Online Version

[![https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>](https://img.shields.io/badge/PHYS3070-Course_Notes-blue)](https://ANU-RSES-Education.github.io/PHYS-3070/book)

For this example, you can see the [online version](https://anu-rses-education.github.io/PHYS-3070/index.html) which is automatically built by github using this repository.

## Local Development

### Building the book

The book uses Quarto with interactive Python examples powered by pyodide (Python in the browser via WebAssembly).

To build the book:

```bash
quarto render
```

The built book will be in `_build/book/`.

### Previewing the book locally

Because the book uses pyodide for interactive Python examples, you need to serve it over HTTP (not just open the HTML files directly). Use the included server script:

```bash
python serve-book.py
```

This will:
- Start a local HTTP server (default port 8000)
- Automatically open your browser to view the book
- Auto-select an available port if 8000 is in use

Press `Ctrl+C` to stop the server.

### Requirements

- Quarto
- Python 3.x (for the preview server)
<!--
## Try out the Jupyterhub


You can launch this example particular example to try it out by clicking on this link. Your work is persistent.

[![https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>](https://img.shields.io/badge/Launch-Demo-blue)](https://phys3070-2021.rses.underworldcloud.org/hub/user-redirect/git-pull?repo=https://github.com/ANU-RSES-Education/PHYS-3070&urlpath=tree/PHYS-3070/StartHere.ipynb&branch=master)
-->

<!--

## Administration tasks

If the hub has a signup page it can be reached here:

[![Signup](https://img.shields.io/badge/User-Signup-blue)](https://test.rses.underworldcloud.org/hub/signup)

And the corresponding page for an admin user to authorise the users after they sign-up is

[![Authorize](https://img.shields.io/badge/Admin-Authorize-Red)](https://test.rses.underworldcloud.org/hub/authorize)

-->

<!--
Admin users have access to the hub control panel to shut down wayward servers and add / remove users.

[![ControlPanel](https://img.shields.io/badge/Admin-HubControlPanel-Red)](https://phys3070-2021.rses.underworldcloud.org/hub/admin)


To make a "binder-like" link to a files in a repository on this droplet, you can read the [nbgitpuller documentation](https://jupyterhub.github.io/nbgitpuller/link.html) or fill out a form here:

 [![https://img.shields.io/badge/<LABEL>-<MESSAGE>-<COLOR>](https://img.shields.io/badge/Admin-LinkMaker-Red)](https://jupyterhub.github.io/nbgitpuller/link.html?hub=https://phys3070-2021.rses.underworldcloud.org&repo=https://github.com/ANU-RSES-Education/PHYS-3070)
-->
