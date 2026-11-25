# Part review of `reference/physics`

No corrections: the property ranges of `PhysicsComponents.cpp`, the automatic room (`ResolveCapacities`: twice the bodies to a power of two, at least 1,024; contacts twice the bodies, at least 2,048), the reserve estimate and its worked case, the 128 worlds, 2^17 and 2^18 reserved at creation, the hull counts 64 and 44, the 4,096 shared box hulls, the 16 change rounds, `MeshWaitTimeout` and `CollisionSteps` agree with the pin and the part.
