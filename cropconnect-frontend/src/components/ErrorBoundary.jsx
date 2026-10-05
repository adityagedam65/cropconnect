// Catches rendering failures so one dashboard panel cannot crash the full page.
import { Component } from "react";
import { RefreshCw } from "lucide-react";

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorKey: 0 };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    console.error("Dashboard panel failed:", error, info);
  }

  handleReset = () => {
    this.setState((prev) => ({ hasError: false, errorKey: prev.errorKey + 1 }));
  };

  render() {
    if (this.state.hasError) {
      return (
        <div className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800 flex items-start gap-3">
          <div className="flex-1">
            <p className="font-medium">This panel could not be loaded.</p>
            <p className="mt-1 text-red-700/70 text-xs">There was a rendering error. Try refreshing this panel.</p>
          </div>
          <button
            onClick={this.handleReset}
            className="shrink-0 flex items-center gap-1.5 rounded-lg border border-red-200 bg-white px-3 py-1.5 text-xs font-medium text-red-700 hover:bg-red-50 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            Try again
          </button>
        </div>
      );
    }

    return (
      <div key={this.state.errorKey}>
        {this.props.children}
      </div>
    );
  }
}
