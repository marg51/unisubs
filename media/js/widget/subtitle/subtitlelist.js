// Universal Subtitles, universalsubtitles.org
// 
// Copyright (C) 2010 Participatory Culture Foundation
// 
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
// 
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see 
// http://www.gnu.org/licenses/agpl-3.0.html.

goog.provide('mirosubs.subtitle.SubtitleList');

/**
 * @param {Array.<mirosubs.subtitle.EditableCaption>} captions
 */
mirosubs.subtitle.SubtitleList = function(captions, displayTimes) {
    goog.ui.Component.call(this);
    this.captions_ = captions;
    this.displayTimes_ = displayTimes;
    this.currentActiveSubtitle_ = null;
    /**
     * A map of captionID to mirosubs.subtitle.SubtitleWidget
     */
    this.subtitleMap_ = {};
    this.currentlyEditing_ = false;
};
goog.inherits(mirosubs.subtitle.SubtitleList, goog.ui.Component);

mirosubs.subtitle.SubtitleList.prototype.createDom = function() {
    this.setElementInternal(this.getDomHelper()
                            .createDom('ul', {'className':'mirosubs-titlesList'}));
    goog.array.forEach(this.captions_, this.addSubtitle, this);
};

/**
 *
 */
mirosubs.subtitle.SubtitleList.prototype.addSubtitle = 
    function(subtitle, opt_scrollDown) {
    var subtitleWidget = new mirosubs.subtitle
    .SubtitleWidget(subtitle, this.displayTimes_, this);
    this.addChild(subtitleWidget, true);
    this.subtitleMap_[subtitle.getCaptionID() + ''] = subtitleWidget;
    if (typeof(opt_scrollDown) == 'boolean' && opt_scrollDown)
        this.scrollToCaption(subtitle.getCaptionID());
};
mirosubs.subtitle.SubtitleList.prototype.clearActiveWidget = function() {
    if (this.currentActiveSubtitle_ != null) {
        this.currentActiveSubtitle_.setActive(false);
        this.currentActiveSubtitle_ = null;
    }
};
mirosubs.subtitle.SubtitleList.prototype.setActiveWidget = function(captionID) {
    this.scrollToCaption(captionID);
    this.clearActiveWidget();
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    subtitleWidget.setActive(true);
    this.currentActiveSubtitle_ = subtitleWidget;
};
mirosubs.subtitle.SubtitleList.prototype.getActiveWidget = function() {
    return this.currentActiveSubtitle_;
};
mirosubs.subtitle.SubtitleList.prototype.scrollToCaption = function(captionID) {
    var subtitleWidget = this.subtitleMap_[captionID + ''];
    goog.style.scrollIntoContainerView(subtitleWidget.getElement(),
                                       this.getElement(), false);
};
mirosubs.subtitle.SubtitleList.prototype.updateWidget = function(captionID) {
    this.subtitleMap_[captionID + ''].updateValues();
};
mirosubs.subtitle.SubtitleList.prototype.setCurrentlyEditing = 
    function(subtitleWidget, editing) {
    this.currentlyEditing_ = editing;
};
mirosubs.subtitle.SubtitleList.prototype.isCurrentlyEditing = function() {
    return this.currentlyEditing_;
};
