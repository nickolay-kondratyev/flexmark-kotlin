plugins {
    java
    `java-library`
    kotlin("jvm") version "2.1.20" apply false
}

allprojects {
    group = "app.thorg.flexmark"
    // Forked from 0.64.8-KMP 0.64.6
    version = "0.1"

    repositories {
        mavenCentral()
    }
}

subprojects {
    apply(plugin = "java-library")
    apply(plugin = "org.jetbrains.kotlin.jvm")

    java {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    tasks.withType<JavaCompile> {
        options.encoding = "UTF-8"
    }

    tasks.withType<org.jetbrains.kotlin.gradle.tasks.KotlinCompile> {
        kotlinOptions {
            jvmTarget = "11"
        }
    }

    // Configure Kotlin source directories
    sourceSets {
        main {
            java.srcDirs("src/main/java", "src/main/kotlin")
        }
        test {
            java.srcDirs("src/test/java", "src/test/kotlin")
        }
    }

    dependencies {
        testImplementation("junit:junit:4.13.2")
        implementation(kotlin("stdlib"))
    }
}
