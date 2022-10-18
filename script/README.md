### Serving locally (system-wide):

- Ruby >=2.7.3 needs to be installed
- Git needs to be installed
- Move this file to the root dir (the clone dir)
- Don't run directly as `root`
- Needs to be executed with sudo permissions
  * Essentially, `sudo ./serve`
- Ignore the errors of "gem update"

### Serving locally (as user only):

- Ruby >=2.7.3 needs to be installed (with sudo)
- Git needs to be installed (with sudo)
- Move this file to the root dir (the clone dir)
- Add the following to your user's `.profile`:

```
GEM_HOME="$(ruby -e 'puts Gem.user_dir')"
PATH="$PATH:$GEM_HOME/bin"
```

### Run the build script:

    > cp ./serve ../../
    > cd thgtoa/
    > sudo ./serve
    [sudo] password for <user>:

    ...snip...

Wait a while for this to finish (first run takes a few minutes).
Now you have updated the gem dependencies.

### Congrats, it's a...bundle:

    Bundle complete! 2 Gemfile dependencies, 92 gems now installed.
    Use `bundle info [gemname]` to see where a bundled gem is installed.

### Serve the site locally:
    > sudo bundle exec jekyll serve
    ...snip ...

        Server address: http://127.0.0.1:4000
      Server running... press ctrl-c to stop.

You are now free to make your desired changes for the guide.  
You can clone remotes and test them here, you can do whatever.

### Non-root user install:

- <https://wiki.archlinux.org/title/ruby#Setup>
- <https://gist.github.com/MichaelCurrin/ddbcfb1714c4dbfb3460a3ecf119620f>
- <https://github.com/MichaelCurrin/learn-to-code/blob/master/en/topics/scripting_languages/Ruby/README.md#install-and-upgrade>
