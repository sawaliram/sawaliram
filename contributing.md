# Contributing code to Sawaliram

Welcome, and thank you for your interest in contributing code to the Sawaliram project! There are many ways to contribute to Sawaliram apart from writing code, like submitting questions, answering questions and translating content. If you would like to get involved with these tasks, send us an email at mail.sawaliram@gmail.com and we will help you get started!

This document provides an overview of our development process and the best practices we are trying to stick to.

## Asking Questions
We use Zulip for discussing the development of the project and asking questions. Make sure you [join our Zulip server](https://sawaliram.zulipchat.com) to get in touch with us quickly and to keep track of the current and future development of the project! Before joining our Zulip server, make sure you read our [code of conduct](https://github.com/sawaliram/sawaliram/blob/master/code_of_conduct.md) guidelines.

## Picking your first issue
We use the GitHub [issue tracker](https://github.com/sawaliram/sawaliram/issues) to keep track of the current and future development works. We keep the issues updated to the discussions on Zulip and it is a definitive place to pick up the next task for yourself! 

Issues marked as [good first issue](https://github.com/sawaliram/sawaliram/labels/good%20first%20issue) are the ones that are suitable for new contributors, although you are free to pick any issue that looks interesting. Once you have read the problem statement described in the issue and think you have a solution, the next step should be either to leave a comment on GitHub, saying you'd like to pick up the issue to work on, or leave a message on the #dev/ stream on Zulip. Feel absolutely free to ask questions or suggest changes or an alternative approach to any problem. We're all here to learn!

## Managing your git repository
Before you start writing any code, you need to make sure you have the latest version of the codebase in your local repository. If you followed the instructions in the README, you will have two remotes in your local git repository - upstream and origin. The upstream remote is the main sawaliram repository which will always have the latest (or 'production') version of the code. Before writing any code, you need to 'sync' your origin with the upstream repository. To do this, run the following commands:
```
$ git checkout master
$ git pull upstream master
```
This command will pull all the changes from the `master` branch of the `upstream` repository and merge it with the `master` branch of your local `origin` repository. 

Now that you have the latest code, it's time to get started with fixing that issue! Let's get started by creating a branch for the issue. You can call your branch anything, but it's always helpful to give a name that indictates which issue this branch is related to. It could be something like 'button-width-fix' (assuming there's an issue which says that some button needs to get it's width fixed). It could even simply have the issue number in the name, for example 'issue-33'. Since the issue tracker has a detailed entry about the issue anyway, this method helps keep the branch names short and consistent. This is completely up to you! To creata a new branch from `master`:
```
$ git checkout -b <branch-name>
``` 
This is the branch that will hold all the changes for this particular issue. You will also use this branch to create a Pull Request once you're ready. To push the changes to this branch in your repository:
```
$ git push origin <branch-name>
```

## Writing good commit messages
Apart from giving information on individual commits, commit messages also tell the story of the project and it's development. We might have to revisit and inspect the commits to maybe find the source of a bug or to see how a particular problem was solved earlier. Therefore, writing good commit messages is almost as important as writing good code. Good news is, you can easily learn how to write good commit messages.

This excellent [post](https://chris.beams.io/posts/git-commit/) takes a deep dive into commit messages. In this document, we will touch on some of the most important things to remember when writing a good commit message:

1. For larger commits, split the commit into a subject line (maximum of 50 characters) and a body (maximum of 72 characters), divided by a blank line:
```
Add wavy borders for the footer

The footer now has a wavy top border, according to the new design. All older footer related CSS has been removed. The footer now uses the existing CSS classes for the text and button styles. 
```
2. Capitalize the subject line and do not end it with a period (.)
3. In the commit message body, describe *what and why* instead of *how*.

4. For smaller commits, like changing a value or fixing typos, you can use the `-m` flag to write a simple commit message inline like so:
```
$ git commit -m "Change the background color of footer to dark grey"
```
5. Use imperative mood for the subject line. Imperative mood simply means that the phrase should sound like a command, for example 'Remove borders on button', 'Change size of headings' are in the imperative mood. To see if you've got it right, try completing the sentence 'If applied, this commit will *your-commit-message*'. For example, 'If applied, this commit will *change the background color of footer to dark grey*'.

## Coding style
To maintain a consistent style across all python code in the project, we use a linter called [Flake8](http://flake8.pycqa.org/en/latest/). There are plugins and extensions for almost all major editors for Flake8 out there. It might be helpful to [read more](https://medium.com/python-pandemonium/what-is-flake8-and-why-we-should-use-it-b89bd78073f2) about Flake8 and Linting in general.

## Creating a Pull Request
Once you are ready with your fix for an issue, the next step is to create a Pull Request on the Sawaliram repo so that the other contributors can look at your code and review it before merging your code to the `master` branch. Having atleast one other developer look at your code could help you improve the code or even your approach to solving problems, coding style, writing commits and pull request messages etc. This is a learning activity, and you should be ready to spend some more time fixing and making changes to your PR before it is merged! 

## Thank You!
Once all the boxes are ticked and your PR is merged, you are officially part of Sawaliram's history. Your code will help answer thousands of questions of eager school students all over India and beyond. Sawaliram salutes your valiant efforts :)
