<script>
	export let name;

	let rand = -1;
    let message = '';
	let src = '';

	function getRand() {
		fetch("./rand")
		    .then(d => d.text())
		    .then(d => (rand = d));
	}

	async function getName() {
		let thisMessage = message;
		let res = await fetch(`./message?name=${message}`);
		let message_recieved = await res.text();
		if (res.ok && thisMessage == message) {
			src = message_recieved;
		}
	}
</script>

<main>
	<h1>Hello {name}!</h1>
	<h1>Your Number is {rand}!</h1>
	<button on:click={getRand}>Get a random number</button>
    <h1>Received Message: {src}</h1>
	<input type="text" placeholder="enter your name" bind:value={message} />
	<button on:click={getName}>Send Message</button>
</main>

<style>
	main {
		text-align: center;
		padding: 1em;
		max-width: 240px;
		margin: 0 auto;
	}

	h1 {
		color: #ff3e00;
		text-transform: uppercase;
		font-size: 4em;
		font-weight: 100;
	}

	@media (min-width: 640px) {
		main {
			max-width: none;
		}
	}
</style>