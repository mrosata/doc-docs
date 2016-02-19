var gulp = require('gulp');
var sass = require('gulp-sass');
var babel = require('gulp-babel');
var sourcemaps = require('gulp-sourcemaps');
var concat = require('gulp-concat');
var browserSync = require('browser-sync').create();
var reload      = browserSync.reload;



/**
 * TASK: "styles"
 *
 *  Turn project SCSS files into vanilla CSS
 *  TODO: Add Autoprefixing to SCSS build
 */
gulp.task('styles', function() {
  return gulp.src('doc_docs/sass/**/*.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./doc_docs/static/css/'));
});


/**
 * TASK: "refresh"
 *
 *  Reload the browser
 */
gulp.task('refresh', function() {
  console.log('Change spotted in the thing, Reloading the first thing using this second thing.');
  return browserSync.reload();
});


/**
 *  TASK: "build"
 *
 *   Watch ES6 files, Build ES5 files with Sourcemaps
 */
gulp.task('build', function compile(watch) {
  return gulp.src('doc_docs/static/js/es6/**.js')
    .pipe(sourcemaps.init())
    .pipe(babel({
      presets: ['es2015']
    }))
    .pipe(concat('app.js'))
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest('doc_docs/static/js/'))
});


/**
 *  TASK: "default"
 *
 *    Setup BrowserSync on localhost which watches the site running on Vagrant Machine.
 *    To watch different host:port just change {.. target: "http://**" ..} to new target.
 *
 *    Watch html, js and css and reload browser accordingly.
 *
 *    Watch ES6 folder for change and then run Babel on it.
 */
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

  // When templates, CSS or JavaScript changes refresh page
  gulp.watch("doc_docs/templates/**/*.html", ['refresh'])
    .on("change", browserSync.reload);
  gulp.watch("doc_docs/static/js/*.js", ['refresh'])
    .on("change", browserSync.reload);
  gulp.watch("doc_docs/static/css/**.css", ['refresh'])
    .on("change", browserSync.reload);

  // When ES6 changes, rebuild then reload
  gulp
    .watch("doc_docs/static/js/es6/**.js", ['build'])
    .on('error', function(err) {
      "use strict";
      console.error(err);
    });
});
