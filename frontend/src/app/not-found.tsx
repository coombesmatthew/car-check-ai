import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function NotFound() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-white flex flex-col">
      <Header />
      <div className="flex-1 flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-7xl font-bold text-blue-600 mb-4">404</p>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Page not found</h1>
          <p className="text-slate-500 mb-8 max-w-md">
            The page you&apos;re looking for doesn&apos;t exist. Try checking a vehicle instead.
          </p>
          <a
            href="/"
            className="inline-block px-8 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
          >
            Check a Vehicle
          </a>
        </div>
      </div>
      <Footer />
    </main>
  );
}
