#!/bin/bash

# Prerequisites:
#  1. git
#  2. ruby
#  3. ruby-dev
#
#  Script MUST be in the root of the git clone directory of your choice.
#  You MUST execute it with elevated privileges.
#
#  When done you can execute these commands:
#  $ bundle exec jekyll serve --livereload (will build and serve the project locally)
#  $ bundle exec jekyll build (will build the site in _site folder)

gem update                  # Errors are safely ignored.
gem install bundler jekyll  # Speaks for itself.
rm -f Gemfile*              # Out with the old..
bundle init                 # ..and in with the new.
rm -rf ./vendor/            # In case `bundle init` above does anything weird.

# Creating the Gemfile we want
cat <<EOF >Gemfile
# frozen_string_literal: true

source "https://rubygems.org"

# gem "rails"

# gem "jekyll", "~> 4.2"
gem "github-pages", group: :jekyll_plugins
gem "jekyll-optional-front-matter", group: :jekyll_plugins
gem "webrick", "~> 1.7"
EOF
bundle install # this will install gems and create a new Gemfile.lock

echo "Now you can test locally:              "
echo "$ bundle exec jekyll serve --livereload"
