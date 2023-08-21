##### Any opinion is welcome.
##### Feel free to discuss in the [discussions] section.
##### Feel free report issues in the [issues] section.

### Code Free Contributions

#### There are multiple ways you can add to the guide:

- You can [submit bugs and feature requests](https://github.com/Anon-Planet/thgtoa/issues/new) with detailed information about your issue or idea:
  - If you'd like to propose an addition, please follow the standards outlined here.
  - If you're reporting an issue, please be sure to include the expected behaviour, the observed behaviour, and steps to reproduce the problem.
- This can require technical knowledge, but you can also get involved in conversations about bug reports and feature requests. This is a great way to get involved without getting too overwhelmed!
- [Help fellow committers test recently submitted pull requests](https://github.com/Anon-Planet/thgtoa/pulls). Simply by pulling down a pull request and testing it, you can help ensure our new code contributions for stability and quality.

### Content Contributions

For those of you who are looking to add content to the guide, include the following:

##### <u>Pull Requests</u>

- **Do** create a [topic branch] to work on instead of working directly on `main`. This helps to:
  - Protect the process.
  - Ensures users are aware of commits on the branch being considered for merge.
  - Allows for a location for more commits to be offered without mingling with other contributor changes.
  - Allows contributors to make progress while a PR is still being reviewed.
- **Do** follow the [50/72 rule] for Git commit messages.
- **Do** write "WIP" on your PR and/or open a [draft PR] if submitting unfinished changes..
- **Do** make sure the title of a draft PR makes it immediately clear that it's a draft
- **Do** target your pull request to the **main branch**.
- **Do** specify a descriptive title to make searching for your pull request easier.
- **Don't** leave your pull request description blank.
- **Don't** abandon your pull request. Being responsive helps us land your changes faster.
- **Don't** post questions in older closed PRs.
- **Do** stick to the guide to find common style issues.
- **Don't** make mass changes (such as replacing "I" with "we") using automated serach/replace functionality.
  - Search/replace doesn't understand context, and as such, will inevitably cause inconsistencies and make the guide harder to read.
  - If it's part of a larger PR, it'll also make the reviewer's life harder, as they'll have to go through manually and undo everything by hand.
  - *If you're going to make mass changes, take the time to do it properly*. Otherwise I'll just have to undo it anyway.
  - If your change contains backslashes (`\`), either escape them with another backslash (`\\`) or put them in a ```code block```.

When reporting guide issues:

- **Do** write a detailed description of your issue and use a descriptive title.
- **Do** make it as detailed as possible and don't just submit 50 line changes without explaining.
- **Don't** file duplicate reports; search for your bug before filing a new report.
- **Don't** attempt to report issues on a closed PR.

### Large PRs

Please split large sets of changes into multiple PRs. For example, a PR that adds Windows 11 support, removes Windows AME references, and fixes typos can be split into 3 PRs. This makes PRs easier to review prior to merging.

For an example of what *not* to do, see: <https://github.com/Anon-Planet/thgtoa/pull/51>. This PR contains enough changes to split into multiple smaller and individually-reviewable PRs.

### Updating PRs

While a PR is being reviewed, modifications may be made to it by the reviewer prior to merging. If this is the case, a new branch will be created for the PR's review. If you would like to submit a change to a PR that is in the process of being reviewed, *do not update the PR directly*. This will only cause merge conflicts and delay the PR from being merged. Instead, submit your changes to the PR's review branch.

For an example of what *not* to do, see: <https://github.com/Anon-Planet/thgtoa/pull/51>. Instead of submitting changes to the PR directly, they should have been submitted as changes to the [PR's associated review branch](https://github.com/NobodySpecial256/thgtoa/tree/pr/51).

---

**Thank you** for taking the few moments to read this far! You're already way ahead of the
curve, so keep it up!

[discussions]: https://github.com/Anon-Planet/thgtoa/discussions
[issues]: https://github.com/Anon-Planet/thgtoa/issues
[help fellow users with open issues]: https://github.com/Anon-Planet/thgtoa/issues
[topic branch]: http://git-scm.com/book/en/Git-Branching-Branching-Workflows#Topic-Branches
[Qubes#7457]: https://github.com/QubesOS/qubes-issues/issues/7457
[50/72 rule]: http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html
[draft pr]: https://help.github.com/en/articles/about-pull-requests#draft-pull-requests
[console output]: https://docs.github.com/en/free-pro-team@latest/github/writing-on-github/creating-and-highlighting-code-blocks#fenced-code-blocks
[verification steps]: https://docs.github.com/en/free-pro-team@latest/github/writing-on-github/basic-writing-and-formatting-syntax#task-lists
[reference associated issues]: https://github.com/blog/1506-closing-issues-via-pull-requests
[help fellow committers test recently submitted pull requests]: https://github.com/Anon-Planet/thgtoa/pulls
