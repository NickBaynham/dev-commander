---
name: dc-branch
description: Branch and pull-request workflow for Dev Commander. Use when the user runs /dc:branch or /dc:pr, or asks to start a feature branch for a plan or open a pull request from completed increments. Prepares branches and PR descriptions; never pushes or merges without explicit user direction.
---

# dc-branch

Team-development workflow around plans. Prepares branches and pull
requests; the user decides when anything leaves the machine (DC9).

## /dc:branch

1. Identify the plan the work belongs to: the active plan by default,
   or the plan the user names.
2. Create and switch to a branch named `dc/NNNN-<slug>` matching the
   plan's filename. If the branch already exists, switch to it.
3. Journal the branch creation with the dc-core journal helper.
   Subsequent /dc:implement increments commit to this branch.

## /dc:pr

1. Confirm the branch's plan has no unchecked increments and the
   latest review verdict is approve, or approve with repairs that
   have been applied.
2. Draft the pull request description from the workspace artifacts:
   a summary from the plan header, a change list and test evidence
   from the increment records, and outcomes from the review reports.
3. Show the draft to the user. Only after they approve: push the
   branch and open the PR with `gh pr create`. Never merge; merging
   is the user's decision in their review tool.
