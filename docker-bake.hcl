variable "TAGS" {
    default = "dev"
}
variable "MULTI_STAGE_TARGET" {
    default = "prod-stage"
}

group "default" {
    targets = ["fd_device", "fd_1wire"]
}

target "default" {
    platforms = ["linux/amd64", "linux/arm64", "linux/arm/v7"]
    context = "."
    pull = true
}

target "fd_device" {
    inherits = ["default"]
    dockerfile = "device/Dockerfile"
    tags = [for tag in split(",", "${TAGS}") : "nstoik/fd_device:${tag}"]
    target = "${MULTI_STAGE_TARGET}"
}

target "fd_1wire" {
    inherits = ["default"]
    dockerfile = "1wire/Dockerfile"
    tags = [for tag in split(",", "${TAGS}") : "nstoik/fd_1wire:${tag}"]
}