import { Refine } from "@refinedev/core";
import { ThemedLayout } from "@refinedev/antd";
import routerProvider from "@refinedev/react-router";
import { BrowserRouter, Routes, Route, Outlet } from "react-router";
import { ConfigProvider, theme } from "antd";

import "@refinedev/antd/dist/reset.css";

import { DatabaseList } from "./pages/DatabaseList";
import { QueryTool } from "./pages/QueryTool";

function App() {
  return (
    <BrowserRouter>
      <ConfigProvider
        theme={{
          algorithm: theme.defaultAlgorithm,
          token: {
            colorPrimary: "#1890ff",
          },
        }}
      >
        <Refine
          routerProvider={routerProvider}
          options={{
            syncWithLocation: true,
            warnWhenUnsavedChanges: true,
          }}
          resources={[
            {
              name: "databases",
              list: "/databases",
            },
          ]}
        >
          <Routes>
            <Route
              element={
                <ThemedLayout>
                  <Outlet />
                </ThemedLayout>
              }
            >
              <Route
                index
                element={
                  <div className="p-8">
                    <h1 className="text-2xl font-bold">DB Query Tool</h1>
                    <p className="mt-4">Welcome to the database query tool</p>
                    <p className="mt-2">
                      <a href="/databases" className="text-blue-500 hover:underline">
                        Manage Databases →
                      </a>
                    </p>
                  </div>
                }
              />
              <Route path="/databases" element={<DatabaseList />} />
              <Route path="/databases/:dbName/query" element={<QueryTool />} />
            </Route>
          </Routes>
        </Refine>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default App;
