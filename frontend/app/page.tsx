import Link from 'next/link';

export default function HomePage() {
    return (
        <main>
            <h1>Welcome to My Next.js App</h1>
            <p>
                Navigate to the <Link href="/snl-tool">SNL Tool</Link> page.
            </p>
        </main>
    );
}

