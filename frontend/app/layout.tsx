import './globals.css';
import { Inter } from "next/font/google";
import classNames from "classnames";
import StackedLayout from "@/app/stacked_layout";

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
    title: "Ledger Analytics",
    description: "",
    icons: {
        icon: "/favicon.png",
    },
};

export default function RootLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <html lang="en" className="h-full">
            <body className={classNames(inter.className, "h-full")}>
                <StackedLayout>{children}</StackedLayout>
            </body>
        </html>
    );
}
