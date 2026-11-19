var gulp = require('gulp');
var $ = require('gulp-load-plugins')();
var merge = require('merge-stream');

var paths = {
    pug: 'partials/*.pug',
    coffee: 'coffee/*.coffee',
    images: 'images/**/*',
    dist: 'dist/'
};

gulp.task('copy-config', function() {
    return gulp.src('openid-auth.json')
        .pipe(gulp.dest(paths.dist));
});

gulp.task('copy-images', function() {
    // gulp 5 reads files as UTF-8 unless told otherwise, which corrupts images
    return gulp.src(paths.images, {encoding: false})
        .pipe(gulp.dest(paths.dist + "images"));
});

// No gulp-plumber: an error must fail the build, not ship an image without the plugin.
gulp.task('compile', function() {
    var pug = gulp.src(paths.pug)
        .pipe($.cached('pug'))
        .pipe($.pug({pretty: true}))
        .pipe($.angularTemplatecache({
            transformUrl: function(url) {
                return '/plugins/openid-auth' + url;
            }
        }))
        .pipe($.remember('pug'));

    var coffee = gulp.src(paths.coffee)
        .pipe($.cached('coffee'))
        .pipe($.coffee())
        .pipe($.remember('coffee'));

    return merge(pug, coffee)
        .pipe($.concat('openid-auth.js'))
        .pipe($.uglify({mangle: false, output: {comments: false}}))
        .pipe(gulp.dest(paths.dist));
});

gulp.task('watch', function() {
    gulp.watch([paths.pug, paths.coffee, paths.images], gulp.series('copy-images', 'compile'));
});

gulp.task('build', gulp.series('copy-config', 'copy-images', 'compile'));

gulp.task('default', gulp.series('build', 'watch'));
