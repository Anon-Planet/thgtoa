# Commit Guide

The Hitchhiker's Guide asks that all commits are structured in a similar way.  
We also suggest signing off on your commits.  
Please review the [CONTRIBUTING.md](../CONTRIBUTING.md) file for detailed contributing guidelines.    
**Your commit will be kicked back if it does not conform.**   
This should be incredibly simple to adopt and adhere to and it takes about 5 minutes to read.     

A typical commit will look like this:

```
<scope>: <subject>

<body>
Fixes #34
Pull Request #35

<notes>
Signed-off-by: Some Name <email>
```

- **Do** double check your commit (if more than one, squash them into one commit).    
- **Do** keep subject lines to a maximum of 60 characters.    
- **Don't** even *think* about putting punctuation (`.!?`) to end your subject line.

## Scope

This is the section of text you'll be altering.  

You will often see things like: `"qubes route: update image between "xxxxxx" and "xxxx"`.  
"Qubes route" is the scope and everything else is the subject line.  
We use this field to group commits by scope when the CHANGELOG is created for a release.  

## Subject

- Subject is a short and concise summary of the change the commit is introducing.  
- This will allow for the scope prefix and decoration in the git-log.  
- It should be in the imperitive form: "add", move, "remove", "edit", and "update" being some examples.  
- Don't bother being incredibly specific; that goes in the body.  
- Just focus on "what" for the subject and "why" for the body.  

## Body

- Body should be full of detail.    
- Explain what this commit is doing and why it is necessary.     
- You may include references to issues and pull requests as well.  
- Our changelog will show references prefixed with "Add", "Remove", and "Edit".     
- Add additional notes *if* they are necessary.  
