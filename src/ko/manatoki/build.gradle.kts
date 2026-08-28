import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    name = "Manatoki"
    versionCode = 4
    contentWarning = ContentWarning.NSFW // or MIXED, please confirm
    libVersion = "1.4"

    source {
        lang = "ko"
        baseUrl = "https://mato30.com/"
        versionId = 2
    }
}
