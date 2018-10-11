path = require 'path'
gulp = require 'gulp'
coffee = require 'gulp-coffee'
webpack = require 'webpack-stream'
cssimport = require 'gulp-cssimport'



gulp.task 'coffee/web', ->
  gulp.src 'src/public/js/*.coffee'
    .pipe coffee()
    .pipe gulp.dest 'build/js/'

gulp.task 'js/web', gulp.series 'coffee/web', ->
  gulp.src ['build/js/index.js']
    .pipe webpack
      resolve:
        modules:[
          "node_modules"
          path.resolve __dirname,"build","js"
        ]
      output:
        filename: 'index.js'
    .pipe gulp.dest 'public/js/'

gulp.task 'css', ->
  gulp.src ['src/public/css/*']
    .pipe cssimport
      includePaths:[
        'build/css',
        'node_modules'
      ]
    .pipe gulp.dest 'public/css'

gulp.task 'html', ->
  gulp.src ['src/public/html/*.html']
    .pipe gulp.dest 'public/'

gulp.task 'coffee/app', ->
  gulp.src 'src/app/*.coffee'
    .pipe coffee()
    .pipe gulp.dest 'app/'

gulp.task 'app', gulp.series 'coffee/app'
gulp.task 'web', gulp.parallel 'js/web','html','css'

gulp.task 'default', gulp.parallel 'app','web'

gulp.task 'watch', ->
  gulp.watch 'src/public/**/*', gulp.parallel 'web'
