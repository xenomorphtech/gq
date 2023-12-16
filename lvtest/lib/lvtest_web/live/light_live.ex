defmodule LvtestWeb.LightLive do
  use LvtestWeb, :live_view

  def mount(_params, _session, socket) do
    socket =
      assign(socket, :new_oauths, [
        %{mail: 1, status: "ok"}
      ])

    socket =
      assign(socket, :past_oauths, [
        %{mail: 2, status: "ok"}
      ])

    if connected?(socket) do
      Process.send_after(self(), :update, 1000)
    end

    socket =
      assign(socket, :x, 1)

    {:ok, socket}
  end

  def render(assigns) do
    ~H"""
    <%= @x %>

    <h1>running google auths</h1>
    <table width="100%">
      <tbody style="border: 1">
        <%= for oauth <- @new_oauths do %>
          <tr>
            <td>
              <%= oauth.mail %>
            </td>
            <td>
              <%= oauth.status %>
            </td>
          </tr>
        <% end %>
      </tbody>
    </table>

    <h1>previous google auths</h1>
    <table width="100%">
      <tbody style="border: 1">
        <%= for oauth <- @past_oauths do %>
          <tr>
            <td>
              <%= oauth.mail %>
            </td>
            <td>
              <%= oauth.status %>
            </td>
          </tr>
        <% end %>
      </tbody>
    </table>
    """
  end

  def handle_event("up", _, socket) do
    socket = update(socket, :brightness, fn b -> b + 10 end)
    {:noreply, socket}
  end

  def handle_info(:update, %{assigns: %{x: x}} = socket) do
    Process.send_after(self(), :update, 1000)
    {:noreply, assign(socket, :x, x + 1)}
  end
end
