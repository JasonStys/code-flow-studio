<?php
/** Jason Stys: trusted auto-prepend coverage hook; targets execute only in restricted workers.
 * State: output path from fixed worker environment; source locations come from Xdebug opcodes.
 * No target file is included by this hook. PHP itself loads the selected entry afterwards.
 * Local symbol map: shutdown callback@L11; $path@L12 is the trusted worker output filename.
 */
if (!function_exists('xdebug_start_code_coverage')) {
    throw new RuntimeException('Xdebug coverage is unavailable');
}
xdebug_start_code_coverage(XDEBUG_CC_UNUSED | XDEBUG_CC_DEAD_CODE);
register_shutdown_function(static function (): void {
    $path = getenv('CFS_COVERAGE_OUTPUT');
    if ($path !== false) {
        file_put_contents($path, json_encode(xdebug_get_code_coverage(), JSON_THROW_ON_ERROR));
    }
});
