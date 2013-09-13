/* jshint node: true */
'use strict';

module.exports = function (grunt) {

    // load all grunt tasks
    require('matchdep').filterDev('grunt-*').forEach(grunt.loadNpmTasks);

    // Project configuration.
    grunt.initConfig({

        // Metadata.
        pkg: grunt.file.readJSON('package.json'),
        banner: '/*!\n' +
                  '* PressHub v<%= pkg.version %> by Ade25\n' +
                  '* Copyright <%= pkg.author %>\n' +
                  '* Licensed under <%= pkg.licenses %>.\n' +
                  '*\n' +
                  '* Designed and built by ade25\n' +
                  '*/\n',
        jqueryCheck: 'if (!jQuery) { throw new Error(\"Bootstrap requires jQuery\") }\n\n',

        // Task configuration.
        clean: {
            dist: ['dist']
        },
        jshint: {
            options: {
                jshintrc: '.jshintrc'
            },
            gruntfile: {
                src: 'Gruntfile.js'
            },
            src: {
                src: ['js/*.js']
            },
            test: {
                src: ['js/tests/unit/*.js']
            }
        },

        concat: {
            options: {
                banner: '<%= banner %><%= jqueryCheck %>',
                stripBanners: false
            },
            bootstrap: {
                src: [
                    'bower_components/jquery/jquery.js',
                    'bower_components/modernizr/modernizr.js',
                    'bower_components/jquery-knob/jquery.knob.js',
                    'bower_components/chosen-sass-bootstrap/chosen.jquery.js',
                    'bower_components/bootstrap/dist/js/bootstrap.js',
                    'bower_components/bootstrap-toggle/js/bootstrap-toggle.js',
                    'bower_components/momentjs/moment.js',
                    'bower_components/momentjs/lang/de.js',
                    'bower_components/livestampjs/livestamp.js',
                    'js/pressapp.js'
                ],
                dest: 'dist/js/presshub.js'
            }
        },

        uglify: {
            options: {
                banner: '<%= banner %>'
            },
            bootstrap: {
                src: ['<%= concat.bootstrap.dest %>'],
                dest: 'dist/js/presshub.min.js'
            }
        },

        recess: {
            options: {
                compile: true
            },
            theme: {
                src: ['less/styles.less'],
                dest: 'dist/css/styles.css'
            },
            min: {
                options: {
                    compress: true
                },
                src: ['less/styles.less'],
                dest: 'dist/css/styles.min.css'
            }
        },

        copy: {
            fonts: {
                expand: true,
                src: ['bower_components/font-awesome/font/*'],
                dest: 'assets/fonts/'
            },
            styles: {
                expand: true,
                flatten: true,
                cwd: 'bower_components/',
                src: ['chosen-sass-bootstrap/chosen/chosen.css'],
                dest: 'assets/css/'
            },
            images: {
                src: ['bower_components/chosen-sass-bootstrap/chosen/chosen-sprite.png'],
                dest: 'assets/img/'
            }
        },

        qunit: {
            options: {
                inject: 'js/tests/unit/phantom.js'
            },
            files: ['js/tests/*.html']
        },

        connect: {
            server: {
                options: {
                    port: 3000,
                    base: '.'
                }
            }
        },

        jekyll: {
            docs: {}
        },

        validation: {
            options: {
                reset: true
            },
            files: {
                src: ['_gh_pages/**/*.html']
            }
        },

        watch: {
            src: {
                files: '<%= jshint.src.src %>',
                tasks: ['jshint:src', 'qunit']
            },
            test: {
                files: '<%= jshint.test.src %>',
                tasks: ['jshint:test', 'qunit']
            },
            recess: {
                files: 'less/*.less',
                tasks: ['recess']
            }
        }
    });


    // These plugins provide necessary tasks.
    grunt.loadNpmTasks('grunt-contrib-clean');
    grunt.loadNpmTasks('grunt-contrib-concat');
    grunt.loadNpmTasks('grunt-contrib-connect');
    grunt.loadNpmTasks('grunt-contrib-copy');
    grunt.loadNpmTasks('grunt-contrib-jshint');
    grunt.loadNpmTasks('grunt-contrib-qunit');
    grunt.loadNpmTasks('grunt-contrib-uglify');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-html-validation');
    grunt.loadNpmTasks('grunt-jekyll');
    grunt.loadNpmTasks('grunt-recess');
    grunt.loadNpmTasks('browserstack-runner');

    // Docs HTML validation task
    grunt.registerTask('validate-html', ['jekyll', 'validation']);

    // Test task.
    var testSubtasks = ['dist-css', 'jshint', 'qunit', 'validate-html'];
    // Only run BrowserStack tests under Travis
    if (process.env.TRAVIS) {
        // Only run BrowserStack tests if this is a mainline commit in twbs/bootstrap, or you have your own BrowserStack key
        if ((process.env.TRAVIS_REPO_SLUG === 'twbs/bootstrap' && process.env.TRAVIS_PULL_REQUEST === 'false') || process.env.TWBS_HAVE_OWN_BROWSERSTACK_KEY) {
            testSubtasks.push('browserstack_runner');
        }
    }
    grunt.registerTask('test', testSubtasks);

    // JS distribution task.
    grunt.registerTask('dist-js', ['concat', 'uglify']);

    // CSS distribution task.
    grunt.registerTask('dist-css', ['recess']);

    // Fonts distribution task.
    grunt.registerTask('dist-assets', ['copy']);

    // Full distribution task.
    grunt.registerTask('dist', ['clean', 'dist-css', 'dist-assets', 'dist-js']);

    // Default task.
    grunt.registerTask('default', ['test', 'dist']);
};