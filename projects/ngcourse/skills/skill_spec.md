# Agent Skills Spec

A skill is a folder of instructions, scripts, and resources that agents can discover and load dynamically to perform better at specific tasks. In order for the folder to be recognized as a skill, it must contain a `SKILL.md` file. 

# Skill Folder Layout

A minimal skill folder looks like this: 

```
my-skill/
  - SKILL.md
  - procedure.py
```

More complex skills can add additional directories and files as needed.


# The SKILL.md file

The skill's "entrypoint" is the `SKILL.md` file. It is the only file required to exist. The file must start with a YAML frontmatter followed by regular Markdown. 

## YAML Frontmatter

The YAML frontmatter has 2 required properties:

- `name`
    - The name of the skill in hyphen-case
    - Restricted to lowercase Unicode alphanumeric + hyphen
    - Must match the name of the directory containing the SKILL.md
- `description` 
    - Description of what the skill does and when Gemini should use it
- `procedure`
    - The relative path to an executable script that performs the skill's actions.