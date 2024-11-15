from typing import Optional
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QMessageBox
from xopt.generators.bayesian.visualize import visualize_generator_model

from badger.routine import Routine


class PlottingArea(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)

        # Create a layout for the plot area without pre-filling it with a plot
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def update_plot(
        self,
        xopt_obj: Optional[Routine],
        variable_names: list[str],
        reference_point: dict[str, float],
        show_acquisition: bool,
        show_samples: bool,
        show_prior_mean: bool,
        show_feasibility: bool,
        n_grid: int,
    ):
        # Clear the existing layout (remove previous plot if any)
        for i in reversed(range(self.layout.count())):
            widget_to_remove = self.layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)

        if not xopt_obj:
            print("Xopt object is not available. Cannot update plot.")
            return

        generator = xopt_obj.generator

        # Ensure use_cuda is a boolean
        generator.use_cuda = False  # or True, depending on your setup

        # Set generator data
        generator.data = xopt_obj.data

        # Check if the model exists
        if not hasattr(generator, "model") or generator.model is None:
            # Attempt to train the model
            print("Model not found. Training the model...")
            try:
                generator.train_model()
            except Exception as e:
                print(f"Failed to train model: {e}")
                QMessageBox.warning(
                    self, "Model Training Error", f"Failed to train model: {e}"
                )
                return

        # Create a new figure and canvas
        figure = Figure()
        canvas = FigureCanvas(figure)

        # Generate the new plot using visualize_generator_model
        fig, ax = visualize_generator_model(
            generator,
            variable_names=variable_names,
            reference_point=reference_point,
            show_acquisition=show_acquisition,
            show_samples=show_samples,
            show_prior_mean=show_prior_mean,
            show_feasibility=show_feasibility,
            n_grid=n_grid,
        )

        # Adjust padding inside the figure
        fig.tight_layout(pad=1)  # Adds padding between plot elements

        # Set the new figure to the canvas and draw it
        canvas.figure = fig
        canvas.draw()

        # Add the new canvas to the layout
        self.layout.addWidget(canvas)

        # Ensure the layout is updated
        self.updateGeometry()
