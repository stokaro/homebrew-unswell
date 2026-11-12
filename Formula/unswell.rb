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
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.9/unswell_0.1.0-alpha.9_darwin_arm64.tar.gz"
      sha256 "450058c9cb60e5a3a7f853be0e433b219834df3e3bc306223aa8e52d94b7bc18"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.9/unswell_0.1.0-alpha.9_darwin_amd64.tar.gz"
      sha256 "45b4354c9c67f427f917e76cf496c91df4414139bbd8ce6397daca3d767de85d"
    end
  end

  on_linux do
    on_arm do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.9/unswell_0.1.0-alpha.9_linux_arm64.tar.gz"
      sha256 "5f4fa2345434add16e298d58ca666edb91cce8521aab7e3cc00f74bb7d0ec53a"
    end
    on_intel do
      url "https://github.com/stokaro/unswell/releases/download/v0.1.0-alpha.9/unswell_0.1.0-alpha.9_linux_amd64.tar.gz"
      sha256 "689bb700781a4f7e2f3a1ae9e519b069c350af69db3ae869087ed862011262d8"
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
