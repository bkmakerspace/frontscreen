gulp = require 'gulp'
coffee = require 'gulp-coffee'
webpack = require 'webpack-stream'
cssimport = require 'gulp-cssimport'

gulp.task 'default', ['app','web']

gulp.task 'app', ['coffee/app']
gulp.task 'web', ['js/web','html','css']

gulp.task 'coffee/web', ->
  gulp.src 'src/public/js/*.coffee'
    .pipe coffee()
    .pipe gulp.dest 'build/js/'

gulp.task 'js/web', ['coffee/web'], ->
  gulp.src ['src/public/js/*.js','build/js/*.js']
    .pipe webpack
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
