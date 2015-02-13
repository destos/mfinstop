module.exports = function (grunt) {

  var appConfig = grunt.file.readJSON('package.json');

  // Load grunt tasks automatically
  // see: https://github.com/sindresorhus/load-grunt-tasks
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  // see: https://npmjs.org/package/time-grunt
  require('time-grunt')(grunt);

  var pathsConfig = function (appName) {
    this.app = appName || appConfig.name;

    return {
      app: this.app,
      templates: this.app + '/templates',
      css: this.app + '/static/css',
      styl: this.app + '/static/styl',
      fonts: this.app + '/static/fonts',
      images: this.app + '/static/images',
      js: this.app + '/static/js',
      manageScript: this.app + '/manage.py'
    };
  };

  grunt.initConfig({

    paths: pathsConfig(),
    pkg: appConfig,

    // see: https://github.com/gruntjs/grunt-contrib-watch
    watch: {
      gruntfile: {
        files: ['Gruntfile.js']
      },
      stylus: {
        files: ['<%= paths.styl %>/**/*.styl'],
        tasks: ['stylus:compile']
      },
      livereload: {
        files: [
          '<%= paths.js %>/**/*.js',
          '<%= paths.styl %>/**/*.styl',
          '<%= paths.app %>/**/*.html'
          ],
        options: {
          spawn: false,
          livereload: true,
        },
      },
    },

    stylus: {
      compile: {
        options: {
          paths: ['<%= paths.styl %>'],
          import: ['variables', 'mixins'],
          // linenos: true,
          compress: false
          // firebug: true
        },
        files: {
          '<%= paths.css %>/main.css': '<%= paths.styl %>/main.styl'
        }
      }
    },

    // see: https://npmjs.org/package/grunt-bg-shell
    bgShell: {
      _defaults: {
        bg: true
      },
      runDjango: {
        cmd: 'python <%= paths.manageScript %> runserver_plus'
      }
    }
  });

  grunt.registerTask('serve', [
    'bgShell:runDjango',
    'watch'
  ]);

  grunt.registerTask('build', [
    'stylus:compile'
  ]);

  grunt.registerTask('default', [
    'build'
  ]);
};
