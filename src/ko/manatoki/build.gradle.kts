import io.github.keiyoushi.gradle.api.ContentWarning

plugins {
    alias(kei.plugins.extension)
}

keiyoushi {
    name = "Manatoki"
    versionCode = 5
    contentWarning = ContentWarning.NSFW // or MIXED, please confirm
    libVersion = "1.4"

    source {
        lang = "ko"
        // Domain rotates often; expose it as an editable "Custom base URL" preference
        // in the extension's settings instead of requiring a rebuild every time.
        baseUrl {
            custom("https://mato30.com/")
        }
        versionId = 2
    }
}
