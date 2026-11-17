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
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.18/unswell_0.1.0-alpha.18_darwin_arm64.tar.gz"
      sha256 "9f7029e10991e38eabbe338b1227256fd52311f4bf507ea4611347a783404a0e"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.18/unswell_0.1.0-alpha.18_darwin_amd64.tar.gz"
      sha256 "e01fcf7383a7b7ee470ef2603e87a35c1bf18f694f8ebce9346b30cfe56b9133"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.18/unswell_0.1.0-alpha.18_linux_arm64.tar.gz"
      sha256 "1b5a29e301b5ba07dac28cf2c10b5d9353bb330d87e8a061afc33427d11f65ca"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.18/unswell_0.1.0-alpha.18_linux_amd64.tar.gz"
      sha256 "e87973abfc1ae4ce96cb1667cd79cb4a04fab26095cc2817a30e5318f45c5a87"
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
