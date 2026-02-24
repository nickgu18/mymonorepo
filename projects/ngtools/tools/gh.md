Work seamlessly with GitHub from the command line.

USAGE
  gh <command> <subcommand> [flags]

CORE COMMANDS
  auth:          Authenticate gh and git with GitHub
  browse:        Open repositories, issues, pull requests, and more in the browser
  codespace:     Connect to and manage codespaces
  gist:          Manage gists
  issue:         Manage issues
  org:           Manage organizations
  pr:            Manage pull requests
  project:       Work with GitHub Projects.
  release:       Manage releases
  repo:          Manage repositories

GITHUB ACTIONS COMMANDS
  cache:         Manage GitHub Actions caches
  run:           View details about workflow runs
  workflow:      View details about GitHub Actions workflows

ALIAS COMMANDS
  co:            Alias for "pr checkout"

ADDITIONAL COMMANDS
  alias:         Create command shortcuts
  api:           Make an authenticated GitHub API request
  attestation:   Work with artifact attestations
  completion:    Generate shell completion scripts
  config:        Manage configuration for gh
  extension:     Manage gh extensions
  gpg-key:       Manage GPG keys
  label:         Manage labels
  preview:       Execute previews for gh features
  ruleset:       View info about repo rulesets
  search:        Search for repositories, issues, and pull requests
  secret:        Manage GitHub secrets
  ssh-key:       Manage SSH keys
  status:        Print information about relevant issues, pull requests, and notifications across repositories
  variable:      Manage GitHub Actions variables

HELP TOPICS
  accessibility: Learn about GitHub CLI's accessibility experiences
  actions:       Learn about working with GitHub Actions
  environment:   Environment variables that can be used with gh
  exit-codes:    Exit codes used by gh
  formatting:    Formatting options for JSON data exported from gh
  mintty:        Information about using gh with MinTTY
  reference:     A comprehensive reference of all gh commands

FLAGS
  --help      Show help for command
  --version   Show gh version

EXAMPLES
  $ gh issue create
  $ gh repo clone cli/cli
  $ gh pr checkout 321

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh auth --help\n\n
Authenticate gh and git with GitHub

USAGE
  gh auth <command> [flags]

AVAILABLE COMMANDS
  login:         Log in to a GitHub account
  logout:        Log out of a GitHub account
  refresh:       Refresh stored authentication credentials
  setup-git:     Setup git with GitHub CLI
  status:        Display active account and authentication state on each known GitHub host
  switch:        Switch active GitHub account
  token:         Print the authentication token gh uses for a hostname and account

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh browse --help\n\n
Transition from the terminal to the web browser to view and interact with:

- Issues
- Pull requests
- Repository content
- Repository home page
- Repository settings


USAGE
  gh browse [<number> | <path> | <commit-sha>] [flags]

FLAGS
  -b, --branch string            Select another branch by passing in the branch name
  -c, --commit string[="last"]   Select another commit by passing in the commit SHA, default is the last commit
  -n, --no-browser               Print destination URL instead of opening the browser
  -p, --projects                 Open repository projects
  -r, --releases                 Open repository releases
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format
  -s, --settings                 Open repository settings
  -w, --wiki                     Open repository wiki

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  A browser location can be specified using arguments in the following format:
  - by number for issue or pull request, e.g. "123"; or
  - by path for opening folders and files, e.g. "cmd/gh/main.go"; or
  - by commit SHA

EXAMPLES
  # Open the home page of the current repository
  $ gh browse
  
  # Open the script directory of the current repository
  $ gh browse script/
  
  # Open issue or pull request 217
  $ gh browse 217
  
  # Open commit page
  $ gh browse 77507cd94ccafcf568f8560cfecde965fcfa63
  
  # Open repository settings
  $ gh browse --settings
  
  # Open main.go at line 312
  $ gh browse main.go:312
  
  # Open main.go with the repository at head of bug-fix branch
  $ gh browse main.go --branch bug-fix
  
  # Open main.go with the repository at commit 775007cd
  $ gh browse main.go --commit=77507cd94ccafcf568f8560cfecde965fcfa63

ENVIRONMENT VARIABLES
  To configure a web browser other than the default, use the BROWSER environment variable.

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh codespace --help\n\n
Connect to and manage codespaces

USAGE
  gh codespace [flags]

ALIASES
  gh cs

AVAILABLE COMMANDS
  code:          Open a codespace in Visual Studio Code
  cp:            Copy files between local and remote file systems
  create:        Create a codespace
  delete:        Delete codespaces
  edit:          Edit a codespace
  jupyter:       Open a codespace in JupyterLab
  list:          List codespaces
  logs:          Access codespace logs
  ports:         List ports in a codespace
  rebuild:       Rebuild a codespace
  ssh:           SSH into a codespace
  stop:          Stop a running codespace
  view:          View details about a codespace

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh gist --help\n\n
Work with GitHub gists.

USAGE
  gh gist <command> [flags]

AVAILABLE COMMANDS
  clone:         Clone a gist locally
  create:        Create a new gist
  delete:        Delete a gist
  edit:          Edit one of your gists
  list:          List your gists
  rename:        Rename a file in a gist
  view:          View a gist

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  A gist can be supplied as argument in either of the following formats:
  - by ID, e.g. 5b0e0062eb8e9654adad7bb1d81cc75f
  - by URL, e.g. "https://gist.github.com/OWNER/5b0e0062eb8e9654adad7bb1d81cc75f"

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh issue --help\n\n
Work with GitHub issues.

USAGE
  gh issue <command> [flags]

GENERAL COMMANDS
  create:        Create a new issue
  list:          List issues in a repository
  status:        Show status of relevant issues

TARGETED COMMANDS
  close:         Close issue
  comment:       Add a comment to an issue
  delete:        Delete issue
  develop:       Manage linked branches for an issue
  edit:          Edit issues
  lock:          Lock issue conversation
  pin:           Pin a issue
  reopen:        Reopen issue
  transfer:      Transfer issue to another repository
  unlock:        Unlock issue conversation
  unpin:         Unpin a issue
  view:          View an issue

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  An issue can be supplied as argument in any of the following formats:
  - by number, e.g. "123"; or
  - by URL, e.g. "https://github.com/OWNER/REPO/issues/123".

EXAMPLES
  $ gh issue list
  $ gh issue create --label bug
  $ gh issue view 123 --web

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh org --help\n\n
Work with GitHub organizations.

USAGE
  gh org <command> [flags]

GENERAL COMMANDS
  list:          List organizations for the authenticated user.

INHERITED FLAGS
  --help   Show help for command

EXAMPLES
  $ gh org list

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh pr --help\n\n
Work with GitHub pull requests.

USAGE
  gh pr <command> [flags]

GENERAL COMMANDS
  create:        Create a pull request
  list:          List pull requests in a repository
  status:        Show status of relevant pull requests

TARGETED COMMANDS
  checkout:      Check out a pull request in git
  checks:        Show CI status for a single pull request
  close:         Close a pull request
  comment:       Add a comment to a pull request
  diff:          View changes in a pull request
  edit:          Edit a pull request
  lock:          Lock pull request conversation
  merge:         Merge a pull request
  ready:         Mark a pull request as ready for review
  reopen:        Reopen a pull request
  review:        Add a review to a pull request
  unlock:        Unlock pull request conversation
  update-branch: Update a pull request branch
  view:          View a pull request

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  A pull request can be supplied as argument in any of the following formats:
  - by number, e.g. "123";
  - by URL, e.g. "https://github.com/OWNER/REPO/pull/123"; or
  - by the name of its head branch, e.g. "patch-1" or "OWNER:patch-1".

EXAMPLES
  $ gh pr checkout 353
  $ gh pr create --fill
  $ gh pr view --web

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh project --help\n\n
Work with GitHub Projects.

The minimum required scope for the token is: `project`.
You can verify your token scope by running `gh auth status` and
add the `project` scope by running `gh auth refresh -s project`.


USAGE
  gh project <command> [flags]

AVAILABLE COMMANDS
  close:         Close a project
  copy:          Copy a project
  create:        Create a project
  delete:        Delete a project
  edit:          Edit a project
  field-create:  Create a field in a project
  field-delete:  Delete a field in a project
  field-list:    List the fields in a project
  item-add:      Add a pull request or an issue to a project
  item-archive:  Archive an item in a project
  item-create:   Create a draft issue item in a project
  item-delete:   Delete an item from a project by ID
  item-edit:     Edit an item in a project
  item-list:     List the items in a project
  link:          Link a project to a repository or a team
  list:          List the projects for an owner
  mark-template: Mark a project as a template
  unlink:        Unlink a project from a repository or a team
  view:          View a project

INHERITED FLAGS
  --help   Show help for command

EXAMPLES
  $ gh project create --owner monalisa --title "Roadmap"
  $ gh project view 1 --owner cli --web
  $ gh project field-list 1 --owner cli
  $ gh project item-list 1 --owner cli

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh release --help\n\n
Manage releases

USAGE
  gh release <command> [flags]

GENERAL COMMANDS
  create:        Create a new release
  list:          List releases in a repository

TARGETED COMMANDS
  delete:        Delete a release
  delete-asset:  Delete an asset from a release
  download:      Download release assets
  edit:          Edit a release
  upload:        Upload assets to a release
  view:          View information about a release

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh repo --help\n\n
Work with GitHub repositories.

USAGE
  gh repo <command> [flags]

GENERAL COMMANDS
  create:        Create a new repository
  list:          List repositories owned by user or organization

TARGETED COMMANDS
  archive:       Archive a repository
  autolink:      Manage autolink references
  clone:         Clone a repository locally
  delete:        Delete a repository
  deploy-key:    Manage deploy keys in a repository
  edit:          Edit repository settings
  fork:          Create a fork of a repository
  gitignore:     List and view available repository gitignore templates
  license:       Explore repository licenses
  rename:        Rename a repository
  set-default:   Configure default repository for this directory
  sync:          Sync a repository
  unarchive:     Unarchive a repository
  view:          View a repository

INHERITED FLAGS
  --help   Show help for command

ARGUMENTS
  A repository can be supplied as an argument in any of the following formats:
  - "OWNER/REPO"
  - by URL, e.g. "https://github.com/OWNER/REPO"

EXAMPLES
  $ gh repo create
  $ gh repo clone cli/cli
  $ gh repo view --web

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh cache --help\n\n
Work with GitHub Actions caches.

USAGE
  gh cache <command> [flags]

AVAILABLE COMMANDS
  delete:        Delete GitHub Actions caches
  list:          List GitHub Actions caches

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

EXAMPLES
  $ gh cache list
  $ gh cache delete --all

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh run --help\n\n
List, view, and watch recent workflow runs from GitHub Actions.

USAGE
  gh run <command> [flags]

AVAILABLE COMMANDS
  cancel:        Cancel a workflow run
  delete:        Delete a workflow run
  download:      Download artifacts generated by a workflow run
  list:          List recent workflow runs
  rerun:         Rerun a run
  view:          View a summary of a workflow run
  watch:         Watch a run until it completes, showing its progress

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh workflow --help\n\n
List, view, and run workflows in GitHub Actions.

USAGE
  gh workflow <command> [flags]

AVAILABLE COMMANDS
  disable:       Disable a workflow
  enable:        Enable a workflow
  list:          List workflows
  run:           Run a workflow by creating a workflow_dispatch event
  view:          View the summary of a workflow

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh co --help\n\n
Check out a pull request in git

USAGE
  gh pr checkout [<number> | <url> | <branch>] [flags]

FLAGS
  -b, --branch string        Local branch name to use (default [the name of the head branch])
      --detach               Checkout PR with a detached HEAD
  -f, --force                Reset the existing local branch to the latest state of the pull request
      --recurse-submodules   Update all submodules after checkout

INHERITED FLAGS
      --help                     Show help for command
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

EXAMPLES
  # Interactively select a PR from the 10 most recent to check out
  $ gh pr checkout
  
  # Checkout a specific PR
  $ gh pr checkout 32
  $ gh pr checkout https://github.com/OWNER/REPO/pull/32
  $ gh pr checkout feature

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh alias --help\n\n
Aliases can be used to make shortcuts for gh commands or to compose multiple commands.

Run `gh help alias set` to learn more.


USAGE
  gh alias <command> [flags]

AVAILABLE COMMANDS
  delete:        Delete set aliases
  import:        Import aliases from a YAML file
  list:          List your aliases
  set:           Create a shortcut for a gh command

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh api --help\n\n
Makes an authenticated HTTP request to the GitHub API and prints the response.

The endpoint argument should either be a path of a GitHub API v3 endpoint, or
`graphql` to access the GitHub API v4.

Placeholder values `{owner}`, `{repo}`, and `{branch}` in the endpoint
argument will get replaced with values from the repository of the current
directory or the repository specified in the `GH_REPO` environment variable.
Note that in some shells, for example PowerShell, you may need to enclose
any value that contains `{...}` in quotes to prevent the shell from
applying special meaning to curly braces.

The `-p/--preview` flag enables opting into previews, which are feature-flagged,
experimental API endpoints or behaviors. The API expects opt-in via the `Accept`
header with format `application/vnd.github.<preview-name>-preview+json` and this
command facilitates that via `--preview <preview-name>`. To send a request for
the corsair and scarlet witch previews, you could use `-p corsair,scarlet-witch`
or `--preview corsair --preview scarlet-witch`.

The default HTTP request method is `GET` normally and `POST` if any parameters
were added. Override the method with `--method`.

Pass one or more `-f/--raw-field` values in `key=value` format to add static string
parameters to the request payload. To add non-string or placeholder-determined values, see
`-F/--field` below. Note that adding request parameters will automatically switch the
request method to `POST`. To send the parameters as a `GET` query string instead, use
`--method GET`.

The `-F/--field` flag has magic type conversion based on the format of the value:

- literal values `true`, `false`, `null`, and integer numbers get converted to
  appropriate JSON types;
- placeholder values `{owner}`, `{repo}`, and `{branch}` get populated with values
  from the repository of the current directory;
- if the value starts with `@`, the rest of the value is interpreted as a
  filename to read the value from. Pass `-` to read from standard input.

For GraphQL requests, all fields other than `query` and `operationName` are
interpreted as GraphQL variables.

To pass nested parameters in the request payload, use `key[subkey]=value` syntax when
declaring fields. To pass nested values as arrays, declare multiple fields with the
syntax `key[]=value1`, `key[]=value2`. To pass an empty array, use `key[]` without a
value.

To pass pre-constructed JSON or payloads in other formats, a request body may be read
from file specified by `--input`. Use `-` to read from standard input. When passing the
request body this way, any parameters specified via field flags are added to the query
string of the endpoint URL.

In `--paginate` mode, all pages of results will sequentially be requested until
there are no more pages of results. For GraphQL requests, this requires that the
original query accepts an `$endCursor: String` variable and that it fetches the
`pageInfo{ hasNextPage, endCursor }` set of fields from a collection. Each page is a separate
JSON array or object. Pass `--slurp` to wrap all pages of JSON arrays or objects
into an outer JSON array.

For more information about output formatting flags, see `gh help formatting`.

USAGE
  gh api <endpoint> [flags]

FLAGS
      --cache duration        Cache the response, e.g. "3600s", "60m", "1h"
  -F, --field key=value       Add a typed parameter in key=value format
  -H, --header key:value      Add a HTTP request header in key:value format
      --hostname string       The GitHub hostname for the request (default "github.com")
  -i, --include               Include HTTP response status line and headers in the output
      --input file            The file to use as body for the HTTP request (use "-" to read from standard input)
  -q, --jq string             Query to select values from the response using jq syntax
  -X, --method string         The HTTP method for the request (default "GET")
      --paginate              Make additional HTTP requests to fetch all pages of results
  -p, --preview strings       Opt into GitHub API previews (names should omit '-preview')
  -f, --raw-field key=value   Add a string parameter in key=value format
      --silent                Do not print the response body
      --slurp                 Use with "--paginate" to return an array of all pages of either JSON arrays or objects
  -t, --template string       Format JSON output using a Go template; see "gh help formatting"
      --verbose               Include full HTTP request and response in the output

INHERITED FLAGS
  --help   Show help for command

EXAMPLES
  # List releases in the current repository
  $ gh api repos/{owner}/{repo}/releases
  
  # Post an issue comment
  $ gh api repos/{owner}/{repo}/issues/123/comments -f body='Hi from CLI'
  
  # Post nested parameter read from a file
  $ gh api gists -F 'files[myfile.txt][content]=@myfile.txt'
  
  # Add parameters to a GET request
  $ gh api -X GET search/issues -f q='repo:cli/cli is:open remote'
  
  # Set a custom HTTP header
  $ gh api -H 'Accept: application/vnd.github.v3.raw+json' ...
  
  # Opt into GitHub API previews
  $ gh api --preview baptiste,nebula ...
  
  # Print only specific fields from the response
  $ gh api repos/{owner}/{repo}/issues --jq '.[].title'
  
  # Use a template for the output
  $ gh api repos/{owner}/{repo}/issues --template \
    '{{range .}}{{.title}} ({{.labels | pluck "name" | join ", " | color "yellow"}}){{"\n"}}{{end}}'
  
  # Update allowed values of the "environment" custom property in a deeply nested array
  $ gh api -X PATCH /orgs/{org}/properties/schema \
     -F 'properties[][property_name]=environment' \
     -F 'properties[][default_value]=production' \
     -F 'properties[][allowed_values][]=staging' \
     -F 'properties[][allowed_values][]=production'
  
  # List releases with GraphQL
  $ gh api graphql -F owner='{owner}' -F name='{repo}' -f query='
    query($name: String!, $owner: String!) {
      repository(owner: $owner, name: $name) {
        releases(last: 3) {
          nodes { tagName }
        }
      }
    }
  '
  
  # List all repositories for a user
  $ gh api graphql --paginate -f query='
    query($endCursor: String) {
      viewer {
        repositories(first: 100, after: $endCursor) {
          nodes { nameWithOwner }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  '
  
  # Get the percentage of forks for the current user
  $ gh api graphql --paginate --slurp -f query='
    query($endCursor: String) {
      viewer {
        repositories(first: 100, after: $endCursor) {
          nodes { isFork }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
      }
    }
  ' | jq 'def count(e): reduce e as $_ (0;.+1);
  [.[].data.viewer.repositories.nodes[]] as $r | count(select($r[].isFork))/count($r[])'

ENVIRONMENT VARIABLES
  GH_TOKEN, GITHUB_TOKEN (in order of precedence): an authentication token for
  `github.com` API requests.
  
  GH_ENTERPRISE_TOKEN, GITHUB_ENTERPRISE_TOKEN (in order of precedence): an
  authentication token for API requests to GitHub Enterprise.
  
  GH_HOST: make the request to a GitHub host other than `github.com`.

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh attestation --help\n\n
Download and verify artifact attestations.


USAGE
  gh attestation [subcommand] [flags]

ALIASES
  gh at

AVAILABLE COMMANDS
  download:      Download an artifact's attestations for offline use
  trusted-root:  Output trusted_root.jsonl contents, likely for offline verification
  verify:        Verify an artifact's integrity using attestations

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh completion --help\n\n
Generate shell completion scripts for GitHub CLI commands.

When installing GitHub CLI through a package manager, it's possible that
no additional shell configuration is necessary to gain completion support. For
Homebrew, see <https://docs.brew.sh/Shell-Completion>

If you need to set up completions manually, follow the instructions below. The exact
config file locations might vary based on your system. Make sure to restart your
shell before testing whether completions are working.

### bash

First, ensure that you install `bash-completion` using your package manager.

After, add this to your `~/.bash_profile`:

	eval "$(gh completion -s bash)"

### zsh

Generate a `_gh` completion script and put it somewhere in your `$fpath`:

	gh completion -s zsh > /usr/local/share/zsh/site-functions/_gh

Ensure that the following is present in your `~/.zshrc`:

	autoload -U compinit
	compinit -i

Zsh version 5.7 or later is recommended.

### fish

Generate a `gh.fish` completion script:

	gh completion -s fish > ~/.config/fish/completions/gh.fish

### PowerShell

Open your profile script with:

	mkdir -Path (Split-Path -Parent $profile) -ErrorAction SilentlyContinue
	notepad $profile

Add the line and save the file:

	Invoke-Expression -Command $(gh completion -s powershell | Out-String)


USAGE
  gh completion -s <shell>

FLAGS
  -s, --shell string   Shell type: {bash|zsh|fish|powershell}

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh config --help\n\n
Display or change configuration settings for gh.

Current respected settings:
- `git_protocol`: the protocol to use for git clone and push operations `{https | ssh}` (default `https`)
- `editor`: the text editor program to use for authoring text
- `prompt`: toggle interactive prompting in the terminal `{enabled | disabled}` (default `enabled`)
- `prefer_editor_prompt`: toggle preference for editor-based interactive prompting in the terminal `{enabled | disabled}` (default `disabled`)
- `pager`: the terminal pager program to send standard output to
- `http_unix_socket`: the path to a Unix socket through which to make an HTTP connection
- `browser`: the web browser to use for opening URLs
- `color_labels`: whether to display labels using their RGB hex color codes in terminals that support truecolor `{enabled | disabled}` (default `disabled`)
- `accessible_colors`: whether customizable, 4-bit accessible colors should be used `{enabled | disabled}` (default `disabled`)
- `accessible_prompter`: whether an accessible prompter should be used `{enabled | disabled}` (default `disabled`)
- `spinner`: whether to use a animated spinner as a progress indicator `{enabled | disabled}` (default `enabled`)


USAGE
  gh config <command> [flags]

AVAILABLE COMMANDS
  clear-cache:   Clear the cli cache
  get:           Print the value of a given configuration key
  list:          Print a list of configuration keys and values
  set:           Update configuration with a value for the given key

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh extension --help\n\n
GitHub CLI extensions are repositories that provide additional gh commands.

The name of the extension repository must start with `gh-` and it must contain an
executable of the same name. All arguments passed to the `gh <extname>` invocation
will be forwarded to the `gh-<extname>` executable of the extension.

An extension cannot override any of the core gh commands. If an extension name conflicts
with a core gh command, you can use `gh extension exec <extname>`.

When an extension is executed, gh will check for new versions once every 24 hours and display
an upgrade notice. See `gh help environment` for information on disabling extension notices.

For the list of available extensions, see <https://github.com/topics/gh-extension>.


USAGE
  gh extension [flags]

ALIASES
  gh extensions, gh ext

AVAILABLE COMMANDS
  browse:        Enter a UI for browsing, adding, and removing extensions
  create:        Create a new extension
  exec:          Execute an installed extension
  install:       Install a gh extension from a repository
  list:          List installed extension commands
  remove:        Remove an installed extension
  search:        Search extensions to the GitHub CLI
  upgrade:       Upgrade installed extensions

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh gpg-key --help\n\n
Manage GPG keys registered with your GitHub account.

USAGE
  gh gpg-key <command> [flags]

AVAILABLE COMMANDS
  add:           Add a GPG key to your GitHub account
  delete:        Delete a GPG key from your GitHub account
  list:          Lists GPG keys in your GitHub account

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh label --help\n\n
Work with GitHub labels.

USAGE
  gh label <command> [flags]

AVAILABLE COMMANDS
  clone:         Clones labels from one repository to another
  create:        Create a new label
  delete:        Delete a label from a repository
  edit:          Edit a label
  list:          List labels in a repository

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh preview --help\n\n
Preview commands are for testing, demonstrative, and development purposes only.
They should be considered unstable and can change at any time.


USAGE
  gh preview <command> [flags]

AVAILABLE COMMANDS
  prompter:      Execute a test program to preview the prompter

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh ruleset --help\n\n
Repository rulesets are a way to define a set of rules that apply to a repository.
These commands allow you to view information about them.


USAGE
  gh ruleset <command> [flags]

ALIASES
  gh rs

AVAILABLE COMMANDS
  check:         View rules that would apply to a given branch
  list:          List rulesets for a repository or organization
  view:          View information about a ruleset

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

EXAMPLES
  $ gh ruleset list
  $ gh ruleset view --repo OWNER/REPO --web
  $ gh ruleset check branch-name

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh search --help\n\n
Search across all of GitHub.

Excluding search results that match a qualifier

In a browser, the GitHub search syntax supports excluding results that match a search qualifier
by prefixing the qualifier with a hyphen. For example, to search for issues that
do not have the label "bug", you would use `-label:bug` as a search qualifier.

`gh` supports this syntax in `gh search` as well, but it requires extra
command line arguments to avoid the hyphen being interpreted as a command line flag because it begins with a hyphen.

On Unix-like systems, you can use the `--` argument to indicate that
the arguments that follow are not a flag, but rather a query string. For example:

$ gh search issues -- "my-search-query -label:bug"

On PowerShell, you must use both the `--%` argument and the `--` argument to
produce the same effect. For example:

$ gh --% search issues -- "my search query -label:bug"

See the following for more information:
- GitHub search syntax: <https://docs.github.com/en/search-github/getting-started-with-searching-on-github/understanding-the-search-syntax#exclude-results-that-match-a-qualifier>
- The PowerShell stop parse flag `--%`: <https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_parsing?view=powershell-7.5#the-stop-parsing-token>
- The Unix-like `--` argument: <https://www.gnu.org/software/bash/manual/bash.html#Shell-Builtin-Commands-1>


USAGE
  gh search <command> [flags]

AVAILABLE COMMANDS
  code:          Search within code
  commits:       Search for commits
  issues:        Search for issues
  prs:           Search for pull requests
  repos:         Search for repositories

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh secret --help\n\n
Secrets can be set at the repository, or organization level for use in
GitHub Actions or Dependabot. User, organization, and repository secrets can be set for
use in GitHub Codespaces. Environment secrets can be set for use in
GitHub Actions. Run `gh help secret set` to learn how to get started.


USAGE
  gh secret <command> [flags]

AVAILABLE COMMANDS
  delete:        Delete secrets
  list:          List secrets
  set:           Create or update secrets

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh ssh-key --help\n\n
Manage SSH keys registered with your GitHub account.

USAGE
  gh ssh-key <command> [flags]

AVAILABLE COMMANDS
  add:           Add an SSH key to your GitHub account
  delete:        Delete an SSH key from your GitHub account
  list:          Lists SSH keys in your GitHub account

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh status --help\n\n
The status command prints information about your work on GitHub across all the repositories you're subscribed to, including:

- Assigned Issues
- Assigned Pull Requests
- Review Requests
- Mentions
- Repository Activity (new issues/pull requests, comments)


USAGE
  gh status [flags]

FLAGS
  -e, --exclude strings   Comma separated list of repos to exclude in owner/name format
  -o, --org string        Report status within an organization

INHERITED FLAGS
  --help   Show help for command

EXAMPLES
  $ gh status -e cli/cli -e cli/go-gh # Exclude multiple repositories
  $ gh status -o cli # Limit results to a single organization

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

\n\n## gh variable --help\n\n
Variables can be set at the repository, environment or organization level for use in
GitHub Actions or Dependabot. Run `gh help variable set` to learn how to get started.


USAGE
  gh variable <command> [flags]

AVAILABLE COMMANDS
  delete:        Delete variables
  get:           Get variables
  list:          List variables
  set:           Create or update variables

FLAGS
  -R, --repo [HOST/]OWNER/REPO   Select another repository using the [HOST/]OWNER/REPO format

INHERITED FLAGS
  --help   Show help for command

LEARN MORE
  Use `gh <command> <subcommand> --help` for more information about a command.
  Read the manual at https://cli.github.com/manual
  Learn about exit codes using `gh help exit-codes`
  Learn about accessibility experiences using `gh help accessibility`

