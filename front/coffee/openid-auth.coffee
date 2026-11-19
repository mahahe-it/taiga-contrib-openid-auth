###
# Copyright (C) 2014-2017 Andrey Antukh <niwi@niwi.nz>
# Copyright (C) 2014-2017 Jesús Espino Garcia <jespinog@gmail.com>
# Copyright (C) 2014-2017 David Barragán Merino <bameda@dbarragan.com>
# Copyright (C) 2014-2017 Alejandro Alonso <alejandro.alonso@kaleidos.net>
# Copyright (C) 2014-2017 Juan Francisco Alcántara <juanfran.alcantara@kaleidos.net>
# Copyright (C) 2014-2017 Xavi Julian <xavier.julian@kaleidos.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# File: openid-auth.coffee
###

OpenIDLoginButtonDirective = ($window, $params, $location, $config, $events, $confirm,
	$auth, $navUrls, $loader) ->
	# Login or registar a user with his/her openid account.
	#
	# Example:
	#	 tg-openid-login-button()
	#
	# Requirements:
	#   - ...

	link = ($scope, $el, $attrs) ->
		AUTH_URL = $config.get("openidAuth", null)
		AUTH_SCOPE = $config.get("openidScope", "openid email")
		CLIENT_ID = $config.get("openidClientId", "taiga")
		$scope.openid_name = $config.get("openidName", "openid-connect")
		loginOnSuccess = (response) ->
			if $params.next and $params.next != $navUrls.resolve("login")
				nextUrl = $params.next
			else
				nextUrl = $navUrls.resolve("home")

			$events.setupConnection()

			$location.search("next", null)
			$location.search("token", null)
			$location.search("state", null)
			$location.search("code", null)
			$location.path(nextUrl)

		redirectURL = () -> $location.absUrl().split('?')[0]
		loginOnError = (response) ->
			$location.search("state", null)
			$location.search("code", null)
			$loader.pageLoaded()

			if response.data._error_message
				$confirm.notify("light-error", response.data._error_message )
			else
				$confirm.notify("light-error", "Our Oompa Loompas have not been able to get your credentials from OpenID.") #TODO: i18n

		# OAuth `state` (login CSRF protection): random per login attempt, kept in
		# session storage until the provider redirects back. The prefix tells our
		# callbacks apart from those of other auth plugins (e.g. `state=github`).
		STATE_PREFIX = "openid-"
		STATE_KEY = "openidAuthState"
		STATE_ERROR = "OpenID login rejected: the response does not match this login attempt (state). Please sign in again." #TODO: i18n

		newState = ->
			bytes = new Uint8Array(16)
			$window.crypto.getRandomValues(bytes)
			STATE_PREFIX + (("0" + b.toString(16)).slice(-2) for b in bytes).join("")

		# Read once: a state is good for a single callback.
		takeState = ->
			try
				expected = $window.sessionStorage.getItem(STATE_KEY)
				$window.sessionStorage.removeItem(STATE_KEY)
				return expected
			catch error
				return null

		loginWithOpenIDAccount = ->
			state = $params.state
			code = $params.code
			accessToken = $params.access_token
			return if not (code) && not(accessToken)

			if code
				# Another auth plugin's callback: not ours to handle.
				return if state and state.indexOf(STATE_PREFIX) != 0
				expected = takeState()
				if not state or not expected or state != expected
					loginOnError({data: {_error_message: STATE_ERROR}})
					return
				data = {code: code, url:redirectURL()}
			else
				data = {access_token: accessToken, url:redirectURL()}

			$loader.start(true)
			$auth.login(data, "openid").then(loginOnSuccess, loginOnError)

		loginWithOpenIDAccount()


		$el.on "click", ".button-auth", (event) ->
			state = newState()
			$window.sessionStorage.setItem(STATE_KEY, state)
			params =
				redirect_uri: redirectURL()
				client_id: CLIENT_ID
				response_type: "code"
				scope: AUTH_SCOPE
				state: state
			query = ("#{encodeURIComponent(k)}=#{encodeURIComponent(v)}" for own k, v of params).join("&")
			separator = if AUTH_URL.indexOf("?") >= 0 then "&" else "?"
			$window.location.href = AUTH_URL + separator + query

		$scope.$on "$destroy", ->
			$el.off()

	return {
		link: link
		restrict: "EA"
		template: ""
	}

module = angular.module('taigaContrib.openidAuth', [])
module.directive("tgOpenidLoginButton", ["$window", '$routeParams', "$tgLocation", "$tgConfig", "$tgEvents",
	"$tgConfirm", "$tgAuth", "$tgNavUrls", "tgLoader",
	OpenIDLoginButtonDirective])
