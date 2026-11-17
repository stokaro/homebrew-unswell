class Unswell < Formula
  desc "Reduce AI-style wording in source code and documentation"
  homepage "https://github.com/stokaro/unswell"
  license "MIT"

  head do
    url "https://github.com/stokaro/unswell.git", branch: "main"
    depends_on "go" => :build
  end

  depends_on "git"

  # BEGIN RELEASE
  on_macos do
    on_arm do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.19/unswell_0.1.0-alpha.19_darwin_arm64.tar.gz"
      sha256 "d234cf7b1b15851d366d6bf7dfec0f690e2c27fe2ec3ea01103793d243870773"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.19/unswell_0.1.0-alpha.19_darwin_amd64.tar.gz"
      sha256 "a09c0bd21cf24f9a791a8b8b8508be0f52db219c52f16cf635714e09965a43e9"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.19/unswell_0.1.0-alpha.19_linux_arm64.tar.gz"
      sha256 "986d764ef7665cf814ac1a2793d35c7ce5654c49c818f479fccb1d4e1e8b2a35"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.19/unswell_0.1.0-alpha.19_linux_amd64.tar.gz"
      sha256 "ab0d11ecd04032b1d0ca31a4c2db9e40c057e4d2814057bd66646b42a9b2c52d"
    end
  end
  # END RELEASE

  def install
    if build.head?
      ENV["CGO_ENABLED"] = "0"
      system "go", "build", *std_go_args(ldflags: "-X github.com/stokaro/unswell.BuildCommit=#{Utils.git_head}"),
             "./cmd/unswell"
    else
      bin.install "unswell"
    end
    pkgshare.install "THIRD_PARTY_NOTICES.md", "licenses"
  end

  test do
    (testpath/"policy.yaml").write "version: 1\nextends: [builtin:strict-v1]\n"
    (testpath/"clean.md").write "The client opens connections.\n"
    (testpath/"bad.md").write "Certainly! The client opens connections.\n"
    (testpath/"invalid.cs").write 'class Sample { string value = "unfinished'

    system bin/"unswell", "check", "clean.md", "--config", "policy.yaml"
    failure = JSON.parse(shell_output("#{bin}/unswell check bad.md --config policy.yaml --report json:-", 1))
    assert_equal "complete", failure.fetch("status")
    assert_equal false, failure.fetch("gate").fetch("passed")
    error = JSON.parse(shell_output("#{bin}/unswell check invalid.cs --config policy.yaml --report json:-", 2))
    assert_equal false, error.fetch("gate").fetch("passed")
    assert_predicate error.fetch("errors"), :any?
  end
end
