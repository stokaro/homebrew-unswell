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
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.17/unswell_0.1.0-alpha.17_darwin_arm64.tar.gz"
      sha256 "d385a351168aa8cb4ee72ac7b8b98025317f8f95924f6e8da635ffe18bf70890"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.17/unswell_0.1.0-alpha.17_darwin_amd64.tar.gz"
      sha256 "67efac0cc7a256201ade0ef7a4d2ffa48f4815ea32ae4104817ef3897396ecd1"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.17/unswell_0.1.0-alpha.17_linux_arm64.tar.gz"
      sha256 "979bb9ca435b8800d459b52b3561211a15407d51cf183c398b2cba0c96cf06cd"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.17/unswell_0.1.0-alpha.17_linux_amd64.tar.gz"
      sha256 "1433c564184ea7b4fa8075f25894654cd04a4cda2b15de7b7e15f42dae53432a"
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
