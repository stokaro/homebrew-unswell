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
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.22/unswell_0.1.0-alpha.22_darwin_arm64.tar.gz"
      sha256 "c40090ab0aed66d6068968cc49e05b4baa611dad94a467a015e1dead84d55a96"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.22/unswell_0.1.0-alpha.22_darwin_amd64.tar.gz"
      sha256 "435ad40a7edde6779e9a5676c960f75c8987f95bece6fa6fb936c82ad110d34e"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.22/unswell_0.1.0-alpha.22_linux_arm64.tar.gz"
      sha256 "aa2b2c4b6f8721b85ae8cef9a51b7e681076438d31370d1075de1f31831b27cf"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.22/unswell_0.1.0-alpha.22_linux_amd64.tar.gz"
      sha256 "8615d972f672f25726dfd36888348dcb7d9510565af8dd15bdc249c1599ea112"
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
