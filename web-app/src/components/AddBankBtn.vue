<template lang='pug'>
  .plaid-link-wrapper
    b-button.theme-dark-blue.has-text-white(
      @click="handleOnClick"
      ) Connect Bank
</template>

<script>
export default {
    name: 'PlaidLink',
    props: {
        plaidUrl: {
            type: String,
            default: 'https://cdn.plaid.com/link/v2/stable/link-initialize.js'
        },
        env: {
            type: String,
            default: 'sandbox'
        },
        institution: String,
        selectAccount: Boolean,
        token: String,
        product: {
            type: [String, Array],
            default: function () { return ['transactions'] }
        },
        language: String,
        countryCodes: Array,
        isWebView: Boolean,
        clientName: String,
        publicKey: String,
        webhook: String,
        onLoad: Function,
        onSuccess: Function,
        onExit: Function,
        onEvent: Function
    },
    created () {
        this.loadScript(this.plaidUrl)
            .then(this.onScriptLoaded)
            .catch(this.onScriptError)
    },
    beforeDestroy () {
        if (window.linkHandler) {
            window.linkHandler.exit()
        }
    },
    methods: {
        onScriptError (error) {
            console.error('There was an issue loading the link-initialize.js script')
        },
        onScriptLoaded () {
            window.linkHandler = window.Plaid.create({
                clientName: this.clientName,
                env: this.env,
                key: this.publicKey,
                onExit: this.onExit,
                onEvent: this.onEvent,
                onSuccess: this.onSuccess,
                product: this.product,
                selectAccount: this.selectAccount,
                token: this.token,
                webhook: this.webhook
            })
            setTimeout(function(){
              document.getElementById("plaid-link-iframe-1").style.height = "100%";
             }, 4000);
        },
        handleOnClick () {
            const institution = this.institution || null
            if (window.linkHandler) {
                window.linkHandler.open(institution)
            }
        },
        loadScript (src) {
            return new Promise(function (resolve, reject) {
                if (document.querySelector('script[src="' + src + '"]')) {
                    resolve()
                    return
                }

                const el = document.createElement('script')

                el.type = 'text/javascript'
                el.async = true
                el.src = src

                el.addEventListener('load', resolve)
                el.addEventListener('error', reject)
                el.addEventListener('abort', reject)

                document.head.appendChild(el)
            })
        }
    }
}
</script>
<style>
  #plaid-link-iframe-1 iframe {
    height: 100% !important;
  }
  .theme-dark-blue {
    background-color: #1B196B !important;
  }
</style>