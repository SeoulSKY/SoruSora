# Contributing to SoruSora
:+1::tada: First off, thanks for taking the time to contribute! :tada::+1:

We want to make contributing to this project as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## How to Contribute to the codebase
Pull requests are the best way to propose changes to the codebase (we use [Github Flow](https://guides.github.com/introduction/flow/index.html)). We actively welcome your pull requests:

1. Fork the repo and create your branch from `master`.
2. If you've added code that should be tested, add tests.
3. If you've changed APIs, update the documentation.
4. Ensure the test suite passes.
5. Make sure your code lints.
6. Issue that pull request!

## How to localize SoruSora into a different language

Localizing the application is easy and __doesn't require coding__. Follow these steps:

1. Go to `sorusora/locales`, copy the `en` folder and paste it (actually, you can copy any folders other than `en` if you would like).
2. Rename the copied folder with one of the [two-letter ISO 639 codes](https://en.wikipedia.org/wiki/List_of_ISO_639_language_codes). For Chinese, it will be `zh-CN` for `Chinese (Simplified)` and `zh-TW` for `Chinese (Traditional)`
3. Translate the sentences after the `=` signs. The expression that looks like `{ $link }` will be replaced with the actual value when the application runs. Place it anywhere in the sentence where it makes sense.
4. For each folder in `sorusora/docs`, navigate to the deepest folder where you can find `.md` files. Add a new file named `<two-letter ISO 639 code>.md` and translate what's written in `en.md` (or any other `.md` file).

## Report bugs using Github's issues
We use GitHub issues to track public bugs. Report a bug by [opening a new issue](https://github.com/SeoulSKY/SoruSora/issues); it's that easy!

## Write bug reports with detail, background, and sample code
[This is an example](http://stackoverflow.com/q/12488905/180626) of a bug report that I think is not a bad model.

**Great Bug Reports** tend to have:

- A quick summary and/or background
- Steps to reproduce
  - Be specific!
  - Give a sample code if you can. [This stackoverflow question](http://stackoverflow.com/q/12488905/180626) includes sample code that *anyone* with a base R setup can run to reproduce.
- What you expected would happen
- What actually happens
- Notes (possibly including why you think this might be happening, or stuff you tried that didn't work)

People *love* thorough bug reports. I'm not even kidding.

## Use a Consistent Coding Style
Follow [PEP 8 Guidelines](https://peps.python.org/pep-0008/), which are standard coding style guidelines for Python

* You can try running `pylint` for style unification

## Documents

These are the documents that will help understand the codebase

* [discord.py](https://discordpy.readthedocs.io/en/latest/)
* [MongoDB](https://www.mongodb.com/docs/drivers/motor/)
* [Docker](https://docs.docker.com)
* [Argos Translate](https://www.argosopentech.com)
* [Node Character AI](https://github.com/realcoloride/node_characterai)
* [Fluent Runtime](https://projectfluent.org/python-fluent/fluent.runtime/stable/usage.html)

If you have any questions, please don't hesitate to ask. You can contact me via [Discord](https://discord.seoulsky.org) or email: contact@seoulsky.org.

## License
By contributing, you agree that your contributions will be licensed under its MIT License.

## Code of Conduct
Consider reading [Code of Conduct](https://github.com/SeoulSKY/SoruSora/blob/master/docs/CODE_OF_CONDUCT.md).
