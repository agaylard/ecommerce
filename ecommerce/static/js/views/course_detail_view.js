define([
        'jquery',
        'backbone',
        'underscore',
        'underscore.string',
        'moment',
        'raw!templates/course_detail.html',
        'raw!templates/_course_seat.html',
        'raw!templates/_course_credit_seats.html',
        'utils/course_utils',
        'shims/ecommerce'
    ],
    function ($,
              Backbone,
              _,
              _s,
              moment,
              CourseDetailTemplate,
              CourseSeatTemplate,
              CourseCreditSeatsTemplate,
              CourseUtils,
              ecommerce) {
        'use strict';

        return Backbone.View.extend({
            className: 'course-detail-view',

            initialize: function () {
                this.listenTo(this.model, 'change', this.render);
            },

            render: function () {
                var html,
                    verificationDeadline = this.model.get('verification_deadline'),
                    templateData;

                templateData = {
                    course: this.model.attributes,
                    courseType: _s.capitalize(this.model.get('type')),
                    verificationDeadline: verificationDeadline ? moment.utc(verificationDeadline).format('lll z') : null
                };

                html = _.template(CourseDetailTemplate)(templateData);
                this.$el.html(html);

                this.renderSeats();

                return this;
            },

            renderSeats: function () {
                var creditProvider,
                    html = '',
                    seats = CourseUtils.orderSeatsForDisplay(this.model.seats()),
                    $seatHolder = $('.course-seats', this.$el);

                seats = CourseUtils.filterSeats(seats, 'credit');

                _.each(seats.residual, function (seat) {
                    html += _.template(CourseSeatTemplate)({seat: seat, moment: moment});
                });

                if (seats.filtered && seats.filtered.length > 0) {
                    _.each(seats.filtered, function (seat) {
                        creditProvider = ecommerce.credit.providers.get(seat.get('credit_provider'));

                        if (creditProvider) {
                            seat.set('credit_provider', creditProvider.get('display_name'));
                        }
                    });
                    html += _.template(CourseCreditSeatsTemplate)({creditSeats: seats.filtered, moment: moment});
                }

                $seatHolder.html(html);
            }
        });
    }
);
