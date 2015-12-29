var gulp = require('gulp');
var sass = require('gulp-sass');
var browserSync = require('browser-sync').create();
var reload      = browserSync.reload;


gulp.task('styles', function() {
    gulp.src('doc_docs/sass/**/*.scss')
        .pipe(sass().on('error', sass.logError))
        .pipe(gulp.dest('./doc_docs/static/css/'));
});

gulp.task('refresh', function() {
    console.log('Reloading from the thing yo.');
    browserSync.reload();
});

gulp.task('default', function() {
    gulp.watch('doc_docs/sass/**/*.scss', ['styles', 'refresh']);

    // Serve files from the root of this project
    browserSync.init({
        proxy: {
            ui: {port: 3001},
            port:3000,
            target: "http://0.0.0.0:5000",
            middleware: function (req, res, next) {
                console.log(req.url);
                next();
            }
        }
    });

    gulp.watch("doc_docs/templates/**/*.html", ['refresh'])
        .on("change", browserSync.reload);
});


// Save a reference to the `reload` method
