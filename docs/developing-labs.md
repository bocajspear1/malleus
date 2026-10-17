---
icon: lucide/hammer
---

Malleus tries to make lab development as easy and simple as possible. It takes full advantage of Incus's image distribution and pre-made images to accelerate system development. 

## Creating Images

Usually the biggest hurdle for labs is building the system images that students use. This can get very complicated with automated installs and builds of operating systems. The following indicates methods to create images:

### Using `incus-build`

For less-complex lab systems, its recommended[^1] to use [incus-build](https://github.com/bocajspear1/incus-build). This allows you to use a very Dockerfile-like syntax to define the lab system and utilize the pre-existing base images that Incus provides.

You can use the default, built-in labs as a basis for how the format works.

1. Create your Incusfile
2. Build your image with `incus-build -f <FILE> -t <TAG>`

[^1]: This is not an un-biased recommendation, as the author of Malleus also make `incus-build`. It also has no relation to the Incus project itself.

### Other Methods

You could also:

- Manually create an image, but this is hard to share what you did.
- Use [distrobuilder](https://linuxcontainers.org/distrobuilder/introduction/), the tool that Incus uses to build it's own base images. It's a bit more complicated but gives you more flexibility on what the image is.