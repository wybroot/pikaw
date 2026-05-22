package assets

import (
	"context"
	"os"
	"path/filepath"
	"strings"
	"testing"

	"github.com/wybroot/pikaw/internal/models"
)

type testSystemConfigProvider struct {
	config *models.SystemConfig
}

func (p testSystemConfigProvider) GetSystemConfig(context.Context) (*models.SystemConfig, error) {
	return p.config, nil
}

func TestRenderUIFilesInDir(t *testing.T) {
	dir := t.TempDir()
	indexPath := filepath.Join(dir, "index.html")
	src := `<!doctype html>
<title>[[.SystemNameZh]][[if and .SystemNameZh .SystemNameEn]] | [[end]][[.SystemNameEn]]</title>
<script>
window.SystemConfig = {
    SystemNameZh: "[[.SystemNameZh]]",
    SystemNameEn: "[[.SystemNameEn]]",
    ICPCode: "[[.ICPCode]]",
    DefaultView: "[[.DefaultView]]",
    Version: "[[.Version]]",
};
</script>
<script>/*__PIKAW_CUSTOM_JS__*/</script>
<style>/*__PIKAW_CUSTOM_CSS__*/</style>`
	if err := os.WriteFile(indexPath, []byte(src), 0644); err != nil {
		t.Fatal(err)
	}

	provider := testSystemConfigProvider{
		config: &models.SystemConfig{
			SystemNameZh: "PikaW 监控",
			SystemNameEn: "PikaW Monitor",
			ICPCode:      "ICP-1",
			DefaultView:  "grid",
			CustomJS:     `console.log("pikaw");`,
			CustomCSS:    `body { color: red; }`,
			Version:      "v1.2.3",
		},
	}
	if err := RenderUIFilesInDir(dir, provider); err != nil {
		t.Fatal(err)
	}

	rendered, err := os.ReadFile(indexPath)
	if err != nil {
		t.Fatal(err)
	}
	html := string(rendered)
	for _, want := range []string{
		"<title>PikaW 监控 | PikaW Monitor</title>",
		`SystemNameZh: "PikaW 监控"`,
		`Version: "v1.2.3"`,
		`console.log("pikaw");`,
		`body { color: red; }`,
	} {
		if !strings.Contains(html, want) {
			t.Fatalf("rendered index.html missing %q:\n%s", want, html)
		}
	}
	if _, err := os.Stat(filepath.Join(dir, "index.html.tmpl")); err != nil {
		t.Fatal(err)
	}
}
