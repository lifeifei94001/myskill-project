---
name: image-blaster
description: Creates 3D environments, SFX, and meshes from a single image using Claude skills, World Labs, and FAL.
---

# image-blaster

Creates 3D environments, SFX, and meshes from a single image using Claude skills, World Labs, and FAL.
Can take you from an image to a fully meshed 3D environment in < 5 minutes.

## Sub-Skills Included

- `image-blast-project`: Create, inspect, and manage an IMAGE-BLAST project envelope under `worlds/<slug>`.
- `image-blast-uncover`: Main image analysis skill, object generation, plate decisionmaking, and initial scene description.
- `image-blast-plate`: Source cleanup and clean plate generation.
- `image-blast-world`: Generate static 3D environment world via World Labs Marble model.
- `image-blast-3d`: 3D object models creation through Hunyuan 3D / FAL.
- `image-blast-sfx`: Ambient and object-specific sound effects generation via ElevenLabs SFX.
- `image-blast-wildcard`: Wildcard exploration and asset synthesis.
- `image-blast-image-edit`: Precise AI image editing pipeline.
