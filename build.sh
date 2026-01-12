#!/usr/bin/env bash
# __enable_bash_strict_mode__

main() {
  eai2 ./gradlew build
}

main "${@}"
