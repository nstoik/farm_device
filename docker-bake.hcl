variable "TAG" {
    default = "dev"
}
variable "MULTI_STAGE_TARGET" {
    default = "prod-stage"
}

group "default" {
    targets = ["fd_device", "fd_1wire"]
}

target "default" {
    dockerfile = "Dockerfile"
    platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    pull = true
}

target "fd_device" {
    inherits = ["default"]
    context = "device"
    tags = ["nstoik/fd_device:${TAG}"]
    target = "${MULTI_STAGE_TARGET}"
}

target "fd_1wire" {
    inherits = ["default"]
    context = "1wire"
    tags = ["nstoik/fd_1wire:${TAG}"]
}